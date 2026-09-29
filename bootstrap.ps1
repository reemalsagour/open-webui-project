<#
.SYNOPSIS
    One-command deployment of the Internal AI Chat Platform to Azure.

.DESCRIPTION
    Run from the repository root on your Windows computer. It:
      1. checks prerequisites and your Azure login
      2. prepares terraform/terraform.tfvars (only if it does not exist yet)
      3. runs terraform init / validate / plan and asks before applying
      4. uploads the last git commit to the VM
      5. runs scripts/setup.sh on the VM (Docker, Key Vault secrets, containers)
      6. runs scripts/validate.sh and prints the URLs

    It never overwrites an existing terraform.tfvars, and it stops for
    confirmation if the Terraform plan would destroy or replace anything.

.PARAMETER SkipInfra
    Skip Terraform and only redeploy the application to an existing VM.

.PARAMETER VmIp / KeyVaultName / PostgresHost
    With -SkipInfra, pass all three to deploy without a local Terraform state
    (for example from a teammate's computer).

.PARAMETER ResourceGroupName / Location
    Only used when a NEW terraform.tfvars is created. Handy for a test deployment.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1 -SkipInfra

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1 -SkipInfra -VmIp 1.2.3.4 -KeyVaultName kv-example -PostgresHost psql-example.postgres.database.azure.com
#>
[CmdletBinding()]
param(
    [string]$SshKeyPath = (Join-Path $env:USERPROFILE ".ssh\openwebui_key"),
    [string]$AdminUsername = "azureadmin",
    [switch]$SkipInfra,
    [string]$ResourceGroupName,
    [string]$Location,
    [string]$VmIp,
    [string]$KeyVaultName,
    [string]$PostgresHost,
    [string]$AdminEmailParam
)

$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
$TfDir    = Join-Path $RepoRoot "terraform"
$TfVars   = Join-Path $TfDir "terraform.tfvars"

# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
function Write-Step([string]$Text) { Write-Host ""; Write-Host "==> $Text" -ForegroundColor Cyan }
function Write-Ok([string]$Text)   { Write-Host "    [OK] $Text" -ForegroundColor Green }
function Write-Warn([string]$Text) { Write-Host "    [!]  $Text" -ForegroundColor Yellow }
function Fail([string]$Text)       { Write-Host ""; Write-Host "ERROR: $Text" -ForegroundColor Red; exit 1 }

function Test-Exit([string]$What) {
    if ($LASTEXITCODE -ne 0) { throw "$What failed (exit code $LASTEXITCODE)." }
}

function Invoke-Quiet([scriptblock]$Block) {
    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try { & $Block *> $null } finally { $ErrorActionPreference = $old }
}

function Read-Default([string]$Prompt, [string]$Default) {
    $v = Read-Host "$Prompt [$Default]"
    if ([string]::IsNullOrWhiteSpace($v)) { return $Default }
    return $v.Trim()
}

function Read-Secret([string]$Prompt) {
    $s = Read-Host -Prompt $Prompt -AsSecureString
    $b = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($s)
    try { return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($b) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b) }
}

# Passwords end up inside connection URLs and .env files, so keep the character set safe.
function Read-ValidatedPassword([string]$Prompt) {
    while ($true) {
        $p = Read-Secret $Prompt
        if (($p.Length -lt 12) -or ($p -notmatch '^[A-Za-z0-9_.-]+$') -or ($p -cnotmatch '[a-z]') -or ($p -cnotmatch '[A-Z]') -or ($p -notmatch '\d')) {
            Write-Warn "Use 12+ characters: letters, digits, underscore, dot or hyphen only, with at least one uppercase letter, one lowercase letter and one digit."
            continue
        }
        return $p
    }
}

function Test-IpInCidr {
    param([string]$Ip, [string]$Cidr)
    try {
        $parts = $Cidr -split '/'
        if ($parts.Count -ne 2) { return $false }
        $prefixLen = [int]$parts[1]
        if ($prefixLen -eq 0) { return $true }  # 0.0.0.0/0 allows everyone
        $ipBytes  = [System.Net.IPAddress]::Parse($Ip).GetAddressBytes()
        $netBytes = [System.Net.IPAddress]::Parse($parts[0]).GetAddressBytes()
        if ($ipBytes.Length -ne 4 -or $netBytes.Length -ne 4) { return $false }
        [Array]::Reverse($ipBytes); [Array]::Reverse($netBytes)
        $ipInt  = [BitConverter]::ToUInt32($ipBytes, 0)
        $netInt = [BitConverter]::ToUInt32($netBytes, 0)
        $mask = [uint32]([math]::Pow(2, 32) - [math]::Pow(2, 32 - $prefixLen))
        return (($ipInt -band $mask) -eq ($netInt -band $mask))
    } catch { return $false }
}

function Test-AzLogin {
    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        az account show --output none 2>$null
        return ($LASTEXITCODE -eq 0)
    } finally { $ErrorActionPreference = $old }
}

function Invoke-Remote([string]$Command) {
    & ssh @SshArgs "$AdminUsername@$Ip" $Command
    if ($LASTEXITCODE -ne 0) { throw "Remote command failed (exit code $LASTEXITCODE): $Command" }
}

function New-TfVars {
    $pub = (Get-Content -Raw $PubKeyPath).Trim()

    # Public IP for the firewall rules
    $myIp = ""
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $myIp = (Invoke-RestMethod -Uri "https://api.ipify.org" -TimeoutSec 10).ToString().Trim()
    } catch { $myIp = "" }
    $cidrDefault = ""
    if ($myIp) { $cidrDefault = "$myIp/32" }
    while ($true) {
        $cidr = Read-Default "Allowed IP range for SSH and web access (your public IP, e.g. 1.2.3.4/32)" $cidrDefault
        if ($cidr -match '^\d{1,3}(\.\d{1,3}){3}/\d{1,2}$') { break }
        Write-Warn "Enter an IPv4 range such as 1.2.3.4/32."
    }

    $suffix = -join ((48..57) + (97..122) | Get-Random -Count 5 | ForEach-Object { [char]$_ })

    while ($true) {
        $pgName = Read-Default "PostgreSQL server name (must be unique across Azure)" "psql-openwebui-$suffix"
        if ($pgName -cmatch '^[a-z0-9-]{3,63}$') { break }
        Write-Warn "Use 3-63 lowercase letters, digits or hyphens."
    }
    while ($true) {
        $kvName = Read-Default "Key Vault name (must be unique across Azure, 3-24 characters)" "kv-openwebui-$suffix"
        if ($kvName -match '^[a-zA-Z][a-zA-Z0-9-]{1,22}[a-zA-Z0-9]$') { break }
        Write-Warn "Use 3-24 letters, digits or hyphens, starting with a letter."
    }

    while ($true) {
        $adminEmail = Read-Default "Open WebUI admin email (this is your own login, not sent anywhere)" "admin@example.com"
        if ($adminEmail -match '^[^@\s]+@[^@\s]+\.[^@\s]+$') { break }
        Write-Warn "Enter a valid email address, e.g. name@example.com."
    }

    $regionDefault = if ($Location) { $Location } else { "eastus2" }
    $region = Read-Default "Azure region (affects VM/quota availability, especially on student subscriptions)" $regionDefault

    Write-Host ""
    Write-Host "Choose passwords and paste your Gemini key. Input is hidden."
    $pgPassword    = Read-ValidatedPassword "PostgreSQL admin password"
    $adminPassword = Read-ValidatedPassword "Open WebUI admin password"
    while ($true) {
        $gemini = (Read-Secret "Gemini API key").Trim()
        if ($gemini.Length -ge 10) { break }
        Write-Warn "That looks too short for a Gemini API key. Copy it again from Google AI Studio."
    }

    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes)
    $rng.Dispose()
    $jwt = -join ($bytes | ForEach-Object { $_.ToString('x2') })

    $lines = @(
        '# Generated by bootstrap.ps1. Contains secrets. Never commit this file.',
        ('ssh_public_key            = "{0}"' -f $pub),
        ('allowed_ssh_cidr          = "{0}"' -f $cidr),
        ('allowed_web_cidr          = "{0}"' -f $cidr),
        ('location                  = "{0}"' -f $region),
        ('postgresql_server_name    = "{0}"' -f $pgName),
        ('key_vault_name            = "{0}"' -f $kvName),
        ('openwebui_admin_email     = "{0}"' -f $adminEmail),
        ('postgresql_admin_password = "{0}"' -f $pgPassword),
        ('gemini_api_key            = "{0}"' -f $gemini),
        ('jwt_secret_key            = "{0}"' -f $jwt),
        ('openwebui_admin_password  = "{0}"' -f $adminPassword)
    )
    if ($ResourceGroupName) { $lines += ('resource_group_name         = "{0}"' -f $ResourceGroupName) }

    $text = ($lines -join "`n") + "`n"
    [System.IO.File]::WriteAllText($TfVars, $text, (New-Object System.Text.UTF8Encoding($false)))
    Write-Ok "Created terraform/terraform.tfvars (git-ignored, keep it private)."
}

# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
try {
    Write-Host ""
    Write-Host "Internal AI Chat Platform - Azure deployment" -ForegroundColor White

    # 1. Prerequisites ------------------------------------------------
    Write-Step "Checking prerequisites"
    $tools = @(
        @{ Name = "git";        Hint = "winget install Git.Git" },
        @{ Name = "ssh";        Hint = "Settings > Apps > Optional features > OpenSSH Client" },
        @{ Name = "scp";        Hint = "Settings > Apps > Optional features > OpenSSH Client" },
        @{ Name = "ssh-keygen"; Hint = "Settings > Apps > Optional features > OpenSSH Client" }
    )
    if (-not $SkipInfra) {
        $tools += @{ Name = "az";        Hint = "winget install Microsoft.AzureCLI" }
        $tools += @{ Name = "terraform"; Hint = "winget install Hashicorp.Terraform" }
    }
    $missing = @()
    foreach ($t in $tools) {
        if (-not (Get-Command $t.Name -ErrorAction SilentlyContinue)) { $missing += ("{0}  ->  {1}" -f $t.Name, $t.Hint) }
    }
    if ($missing.Count -gt 0) {
        Fail ("Missing tools. Install them, open a new terminal, and run again:`n  " + ($missing -join "`n  "))
    }
    Invoke-Quiet { git -C $RepoRoot rev-parse --is-inside-work-tree }
    if ($LASTEXITCODE -ne 0) { Fail "This script must live inside the git repository (repo root)." }
    Write-Ok "All required tools found."

    # 2. Azure login --------------------------------------------------
    if (-not $SkipInfra) {
        Write-Step "Azure login"
        if (-not (Test-AzLogin)) {
            az login | Out-Null
            Test-Exit "az login"
        }
        $sub = az account show --query "{name:name, id:id}" -o json | ConvertFrom-Json
        Write-Host ("    Subscription: {0} ({1})" -f $sub.name, $sub.id)
        $a = Read-Host "    Deploy into this subscription? [Y/n]"
        if ($a -match '^(n|no)$') { Fail "Run 'az account set --subscription <ID>' and start again." }
    }

    # 3. SSH key ------------------------------------------------------
    Write-Step "SSH key"
    $PubKeyPath = "$SshKeyPath.pub"
    if (-not (Test-Path $SshKeyPath)) {
        if ($SkipInfra) { Fail "SSH private key not found at $SshKeyPath. Pass -SshKeyPath with the key you use for this VM." }
        Write-Host "    No key found. Creating one (press Enter twice to skip the passphrase)."
        New-Item -ItemType Directory -Force -Path (Split-Path $SshKeyPath) | Out-Null
        ssh-keygen -t rsa -b 4096 -f $SshKeyPath
        Test-Exit "ssh-keygen"
    }
    if (-not (Test-Path $PubKeyPath)) { Fail "Public key not found at $PubKeyPath." }
    Write-Ok "Using key $SshKeyPath"

    # 4. Terraform ----------------------------------------------------
    if (-not $SkipInfra) {
        Write-Step "Terraform variables"
        if (Test-Path $TfVars) { Write-Ok "Using existing terraform/terraform.tfvars (not modified)." }
        else { New-TfVars }

        # A stopped PostgreSQL server blocks even 'terraform plan', since Terraform
        # has to read the server's live state. Start it first if needed.
        Write-Step "Checking PostgreSQL server state"
        $pgNameLine = Select-String -Path $TfVars -Pattern 'postgresql_server_name\s*=\s*"([^"]+)"' -ErrorAction SilentlyContinue
        if ($pgNameLine) {
            $pgName = $pgNameLine.Matches[0].Groups[1].Value
            $rgLine = Select-String -Path $TfVars -Pattern 'resource_group_name\s*=\s*"([^"]+)"' -ErrorAction SilentlyContinue
            $rgName = if ($rgLine) { $rgLine.Matches[0].Groups[1].Value } else { "rg-openwebui" }

            $old = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
            $pgState = (az postgres flexible-server show --resource-group $rgName --name $pgName --query "state" -o tsv 2>$null)
            $ErrorActionPreference = $old

            if ($pgState -and ($pgState.Trim() -ne "Ready")) {
                Write-Warn "PostgreSQL server '$pgName' is '$($pgState.Trim())'. Starting it..."
                az postgres flexible-server start --resource-group $rgName --name $pgName | Out-Null
                Test-Exit "az postgres flexible-server start"
                for ($i = 1; $i -le 18; $i++) {
                    Start-Sleep -Seconds 10
                    $pgState = (az postgres flexible-server show --resource-group $rgName --name $pgName --query "state" -o tsv 2>$null)
                    if ($pgState -and ($pgState.Trim() -eq "Ready")) { break }
                    Write-Host "    waiting for PostgreSQL to be ready ($i/18)..."
                }
                if (-not $pgState -or ($pgState.Trim() -ne "Ready")) {
                    Fail "PostgreSQL server '$pgName' did not become ready in time. Check it in the Azure Portal and run this script again."
                }
                Write-Ok "PostgreSQL server is ready."
            } elseif ($pgState) {
                Write-Ok "PostgreSQL server is already running."
            } else {
                Write-Warn "Could not read PostgreSQL server state (it may not exist yet). Continuing."
            }
        }

        Write-Step "Terraform plan"
        Push-Location $TfDir
        try {
            terraform init -input=false
            Test-Exit "terraform init"
            terraform validate
            Test-Exit "terraform validate"
            terraform plan -input=false -out=tfplan
            Test-Exit "terraform plan"

            $plan = terraform show -json tfplan | ConvertFrom-Json
            Test-Exit "terraform show"
            $changes = @($plan.resource_changes | Where-Object {
                ($_.change.actions -notcontains 'no-op') -and ($_.change.actions -notcontains 'read')
            })
            $outputChanges = @($plan.output_changes.PSObject.Properties | Where-Object {
                $_.Value.actions -and ($_.Value.actions -notcontains 'no-op')
            })

            if (($changes.Count -eq 0) -and ($outputChanges.Count -eq 0)) {
                Write-Ok "Infrastructure is already up to date. Nothing to apply."
            } else {
                Write-Host ""
                Write-Host "    Planned changes:"
                foreach ($c in $changes) {
                    Write-Host ("      {0,-16} {1}" -f ($c.change.actions -join '+'), $c.address)
                }
                foreach ($o in $outputChanges) {
                    Write-Host ("      {0,-16} output.{1}" -f ($o.Value.actions -join '+'), $o.Name)
                }
                $destructive = @($changes | Where-Object { $_.change.actions -contains 'delete' })
                Write-Host ""
                if ($destructive.Count -gt 0) {
                    Write-Warn "This plan DESTROYS or REPLACES $($destructive.Count) resource(s) (delete / delete+create above)."
                    Write-Warn "Replacing a VM erases its local files. Replacing PostgreSQL erases the database."
                    $a = Read-Host "    Type DESTROY to continue anyway, or press Enter to cancel"
                    if ($a -cne 'DESTROY') { Fail "Cancelled. Nothing was changed." }
                } else {
                    $a = Read-Host "    Apply these $($changes.Count + $outputChanges.Count) change(s)? [Y/n]"
                    if ($a -match '^(n|no)$') { Fail "Cancelled. Nothing was changed." }
                }
                Write-Step "Terraform apply (PostgreSQL can take 10-15 minutes on a first run)"
                terraform apply -input=false tfplan
                Test-Exit "terraform apply"
            }
        } finally {
            # A saved plan contains secret values, so never leave it behind.
            $planFile = Join-Path $TfDir "tfplan"
            if (Test-Path $planFile) { Remove-Item $planFile -Force }
            Pop-Location
        }
    }

    # 5. Connection details -------------------------------------------
    Write-Step "Reading deployment details"
    if ($VmIp -and $KeyVaultName -and $PostgresHost) {
        $Ip = $VmIp; $VaultName = $KeyVaultName; $PgHost = $PostgresHost
        $AdminEmail = if ($AdminEmailParam) { $AdminEmailParam } else { "admin@yourcompany.com" }
    } else {
        if (-not (Test-Path (Join-Path $TfDir "terraform.tfstate"))) {
            Fail "No Terraform state on this computer. Pass -VmIp, -KeyVaultName and -PostgresHost, or run without -SkipInfra on the computer that created the infrastructure."
        }
        Push-Location $TfDir
        try {
            $Ip = (terraform output -raw public_ip_address | Out-String).Trim();  Test-Exit "terraform output public_ip_address"
            $PgHost = (terraform output -raw postgresql_fqdn | Out-String).Trim(); Test-Exit "terraform output postgresql_fqdn"
            $VaultName = (terraform output -raw key_vault_name | Out-String).Trim(); Test-Exit "terraform output key_vault_name"
            $AdminEmail = (terraform output -raw openwebui_admin_email | Out-String).Trim(); Test-Exit "terraform output openwebui_admin_email"
        } finally { Pop-Location }
    }
    if ($Ip -notmatch '^\d{1,3}(\.\d{1,3}){3}$') { Fail "Unexpected VM address '$Ip'." }
    if (-not $AdminEmail) { Fail "openwebui_admin_email came back empty. Run 'cd terraform; terraform output openwebui_admin_email' to check, and confirm the last 'terraform apply' finished without errors." }
    Write-Ok "VM: $Ip | Key Vault: $VaultName | PostgreSQL: $PgHost | Admin email: $AdminEmail"

    # 5b. Make sure the VM is actually running -------------------------
    # The VM is commonly deallocated between sessions to save Azure credit.
    # A stopped VM makes every SSH attempt below time out with a confusing
    # error, so check and start it here instead.
    Write-Step "Checking VM power state"
    $rgLineVm = if (Test-Path $TfVars) { Select-String -Path $TfVars -Pattern 'resource_group_name\s*=\s*"([^"]+)"' -ErrorAction SilentlyContinue } else { $null }
    $rgNameVm = if ($rgLineVm) { $rgLineVm.Matches[0].Groups[1].Value } else { "rg-openwebui" }
    $vmNameLine = if (Test-Path $TfVars) { Select-String -Path $TfVars -Pattern 'vm_name\s*=\s*"([^"]+)"' -ErrorAction SilentlyContinue } else { $null }
    $vmName = if ($vmNameLine) { $vmNameLine.Matches[0].Groups[1].Value } else { "vm-openwebui" }

    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $vmStatus = (az vm get-instance-view --resource-group $rgNameVm --name $vmName --query "instanceView.statuses[?starts_with(code, 'PowerState/')].displayStatus" -o tsv 2>$null)
    $ErrorActionPreference = $old

    if ($vmStatus -and ($vmStatus.Trim() -ne "VM running")) {
        Write-Warn "VM '$vmName' is '$($vmStatus.Trim())'. Starting it..."
        az vm start --resource-group $rgNameVm --name $vmName | Out-Null
        Test-Exit "az vm start"
        Write-Ok "VM start requested."
    } elseif ($vmStatus) {
        Write-Ok "VM is already running."
    } else {
        Write-Warn "Could not read VM power state. Continuing and letting the SSH check below decide."
    }

    # 5c. Check for the most common silent SSH blocker: your IP changed ----
    # If the machine's public IP no longer matches allowed_ssh_cidr / allowed_web_cidr,
    # SSH and/or the browser will be blocked with no useful error. Catch it here.
    if (Test-Path $TfVars) {
        $currentIp = ""
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            $currentIp = (Invoke-RestMethod -Uri "https://api.ipify.org" -TimeoutSec 10).ToString().Trim()
        } catch { $currentIp = "" }

        if ($currentIp) {
            foreach ($varName in @("allowed_ssh_cidr", "allowed_web_cidr")) {
                $cidrLine = Select-String -Path $TfVars -Pattern "$varName\s*=\s*`"([^`"]+)`"" -ErrorAction SilentlyContinue
                if ($cidrLine) {
                    $cidr = $cidrLine.Matches[0].Groups[1].Value
                    if (-not (Test-IpInCidr -Ip $currentIp -Cidr $cidr)) {
                        Write-Warn "Your current public IP ($currentIp) does not match $varName ($cidr) in terraform.tfvars."
                    }
                }
            }
            $sshLine = Select-String -Path $TfVars -Pattern 'allowed_ssh_cidr\s*=\s*"([^"]+)"' -ErrorAction SilentlyContinue
            if ($sshLine -and -not (Test-IpInCidr -Ip $currentIp -Cidr $sshLine.Matches[0].Groups[1].Value)) {
                Write-Warn "SSH will likely time out. Update allowed_ssh_cidr to $currentIp/32, then run: cd terraform; terraform apply"
                $a = Read-Host "    Continue anyway and try SSH regardless? [y/N]"
                if ($a -notmatch '^(y|yes)$') { Fail "Cancelled. Update allowed_ssh_cidr to $currentIp/32 and re-run terraform apply first." }
            }
        }
    }

    # 6. Wait for SSH -------------------------------------------------
    Write-Step "Connecting to the VM"
    $SshArgs = @('-i', $SshKeyPath, '-o', 'StrictHostKeyChecking=accept-new', '-o', 'ConnectTimeout=10', '-o', 'ServerAliveInterval=30')
    # A recreated VM keeps its IP but gets a new host key; forget the old one.
    Invoke-Quiet { ssh-keygen -R $Ip }
    $ready = $false
    for ($i = 1; $i -le 30; $i++) {
        $old = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        ssh @SshArgs -o BatchMode=yes "$AdminUsername@$Ip" "echo ok" *> $null
        $code = $LASTEXITCODE
        $ErrorActionPreference = $old
        if ($code -eq 0) { $ready = $true; break }
        Write-Host "    waiting for SSH ($i/30)..."
        Start-Sleep -Seconds 10
    }
    if (-not $ready) { Fail "Could not connect over SSH. Check the VM is running and your IP matches allowed_ssh_cidr." }
    Write-Ok "SSH connection works."

    # 7. Upload the code ----------------------------------------------
    Write-Step "Uploading the project (last git commit)"
    $branch = (git -C $RepoRoot rev-parse --abbrev-ref HEAD | Out-String).Trim()
    $commit = (git -C $RepoRoot rev-parse --short HEAD | Out-String).Trim()
    Write-Host "    Deploying commit $commit on branch '$branch'."
    $dirty = git -C $RepoRoot status --porcelain
    if ($dirty) {
        Write-Warn "You have uncommitted changes. They are NOT uploaded, only the last commit is."
        $a = Read-Host "    Continue anyway? [y/N]"
        if ($a -notmatch '^(y|yes)$') { Fail "Cancelled. Commit your changes and run again." }
    }
    $Tar = Join-Path $env:TEMP "open-webui-project.tar"
    git -C $RepoRoot archive --format=tar --prefix=open-webui-project/ -o $Tar HEAD
    Test-Exit "git archive"
    & scp @SshArgs $Tar ("{0}@{1}:/home/{0}/" -f $AdminUsername, $Ip)
    Test-Exit "scp upload"
    Remove-Item $Tar -Force
    # Extract, then strip Windows line endings from every shell script.
    Invoke-Remote 'tar -xf ~/open-webui-project.tar -C ~ && rm -f ~/open-webui-project.tar && find ~/open-webui-project -name ''*.sh'' -exec sed -i ''s/\r$//'' {} +'
    Write-Ok "Project uploaded to ~/open-webui-project"

    # 8. Setup on the VM ----------------------------------------------
    Write-Step "Running setup.sh on the VM (Docker, Key Vault secrets, containers). This takes a few minutes."
    Invoke-Remote "bash ~/open-webui-project/scripts/setup.sh '$VaultName' '$PgHost' '$AdminEmail'"
    Write-Ok "Setup finished."

    # 9. Validate -----------------------------------------------------
    Write-Step "Validating the deployment"
    & ssh @SshArgs "$AdminUsername@$Ip" "bash ~/open-webui-project/scripts/validate.sh"
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "validate.sh reported a problem. Check the output above and run: docker compose logs (in ~/open-webui-project/docker)."
    } else {
        Write-Ok "Validation passed."
    }

    Write-Host ""
    Write-Host "Deployment finished." -ForegroundColor Green
    Write-Host "  Frontend:   http://${Ip}:8501"
    Write-Host "  Open WebUI: http://${Ip}:3000  (admin and testing)"
    Write-Host "  SSH:        ssh -i `"$SshKeyPath`" $AdminUsername@$Ip"
    Write-Host ""
    Write-Host "To pause and save credit:  az vm deallocate --resource-group <RESOURCE_GROUP> --name vm-openwebui"
    Write-Host ""
}
catch {
    Fail $_.Exception.Message
}
