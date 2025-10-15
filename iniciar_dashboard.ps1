# Script de Inicializacao do Dashboard - PowerShell
# Licenciamento Microsoft - Versao Docker

param(
    [Parameter(Position=0)]
    [ValidateSet('start', 'stop', 'restart', 'logs', 'rebuild', 'cleanup', 'status')]
    [string]$Action = 'menu'
)

# Cores para output
function Write-Success { param($Message) Write-Host $Message -ForegroundColor Green }
function Write-Error-Custom { param($Message) Write-Host $Message -ForegroundColor Red }
function Write-Warning-Custom { param($Message) Write-Host $Message -ForegroundColor Yellow }
function Write-Info { param($Message) Write-Host $Message -ForegroundColor Cyan }
function Write-Title { param($Message) Write-Host "`n$('='*80)" -ForegroundColor Cyan; Write-Host $Message -ForegroundColor Cyan; Write-Host $('='*80)`n -ForegroundColor Cyan }

# Banner
function Show-Banner {
    Write-Title "Dashboard de Licenciamento Microsoft - Docker"
}

# Verificar pre-requisitos
function Test-Prerequisites {
    Write-Info "Verificando pre-requisitos..."
    
    # Verificar Docker
    try {
        $dockerVersion = docker --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "[OK] Docker encontrado: $dockerVersion"
        } else {
            throw "Docker nao encontrado"
        }
    } catch {
        Write-Error-Custom "[ERRO] Docker nao esta instalado ou nao esta em execucao!"
        Write-Warning-Custom "`nInstale o Docker Desktop em: https://www.docker.com/products/docker-desktop/"
        exit 1
    }
    
    # Verificar Docker Compose
    try {
        $composeVersion = docker-compose --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "[OK] Docker Compose encontrado: $composeVersion"
        } else {
            throw "Docker Compose nao encontrado"
        }
    } catch {
        Write-Error-Custom "[ERRO] Docker Compose nao esta instalado!"
        exit 1
    }
    
    # Verificar arquivo Excel
    $excelFile = "LICENCIAMENTO MICROSOFT (1).xlsx"
    if (Test-Path $excelFile) {
        Write-Success "[OK] Planilha de dados encontrada: $excelFile"
    } else {
        Write-Error-Custom "[ERRO] Arquivo '$excelFile' nao encontrado!"
        Write-Warning-Custom "Certifique-se de que o arquivo esta no diretorio: $PWD"
        exit 1
    }
    
    Write-Host ""
}

# Menu interativo
function Show-Menu {
    Write-Host "`nEscolha uma opcao:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1" -ForegroundColor Cyan -NoNewline; Write-Host " - Iniciar Dashboard (primeira vez / reconstruir)"
    Write-Host "  2" -ForegroundColor Cyan -NoNewline; Write-Host " - Iniciar Dashboard (rapido - sem rebuild)"
    Write-Host "  3" -ForegroundColor Cyan -NoNewline; Write-Host " - Parar Dashboard"
    Write-Host "  4" -ForegroundColor Cyan -NoNewline; Write-Host " - Ver logs do Dashboard"
    Write-Host "  5" -ForegroundColor Cyan -NoNewline; Write-Host " - Reiniciar Dashboard"
    Write-Host "  6" -ForegroundColor Cyan -NoNewline; Write-Host " - Ver status dos containers"
    Write-Host "  7" -ForegroundColor Cyan -NoNewline; Write-Host " - Remover containers e volumes"
    Write-Host "  0" -ForegroundColor Cyan -NoNewline; Write-Host " - Sair"
    Write-Host ""
}

# Funcoes de controle
function Start-Dashboard {
    param([bool]$Rebuild = $false)
    
    if ($Rebuild) {
        Write-Title "Construindo e iniciando o Dashboard..."
        Write-Warning-Custom "Isso pode levar alguns minutos na primeira vez.`n"
        docker-compose up -d --build
    } else {
        Write-Title "Iniciando o Dashboard..."
        docker-compose up -d
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "`n[OK] Dashboard iniciado com sucesso!"
        Write-Info "`nAcesse em seu navegador: http://localhost:5000"
        Write-Host ""
        
        # Aguardar um pouco e abrir navegador
        Start-Sleep -Seconds 2
        Start-Process "http://localhost:5000"
    } else {
        Write-Error-Custom "`n[ERRO] Falha ao iniciar o Dashboard."
        Write-Warning-Custom "Verifique os logs com a opcao 4 do menu."
    }
}

function Stop-Dashboard {
    Write-Title "Parando o Dashboard..."
    docker-compose stop
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "[OK] Dashboard parado com sucesso!"
    } else {
        Write-Error-Custom "[ERRO] Falha ao parar o Dashboard."
    }
}

function Restart-Dashboard {
    Write-Title "Reiniciando o Dashboard..."
    docker-compose restart
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "`n[OK] Dashboard reiniciado com sucesso!"
        Write-Info "Acesse em seu navegador: http://localhost:5000"
    } else {
        Write-Error-Custom "[ERRO] Falha ao reiniciar o Dashboard."
    }
}

function Show-Logs {
    Write-Title "Logs do Dashboard (Pressione Ctrl+C para sair)"
    docker-compose logs -f
}

function Show-Status {
    Write-Title "Status dos Containers"
    docker-compose ps
    Write-Host ""
    
    Write-Info "Detalhes dos containers:"
    docker ps --filter "name=dashboard" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    Write-Host ""
}

function Remove-Dashboard {
    Write-Warning-Custom "`nATENCAO: Isso vai remover todos os containers e volumes!"
    $confirm = Read-Host "Tem certeza? (S/N)"
    
    if ($confirm -eq 'S' -or $confirm -eq 's') {
        Write-Title "Removendo containers e volumes..."
        docker-compose down -v
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "[OK] Limpeza concluida!"
        } else {
            Write-Error-Custom "[ERRO] Falha na limpeza."
        }
    } else {
        Write-Warning-Custom "Operacao cancelada."
    }
}

# Executar acao
Show-Banner
Test-Prerequisites

# Se foi passado um parametro, executar diretamente
switch ($Action) {
    'start' { 
        Start-Dashboard -Rebuild $false
        exit 0
    }
    'rebuild' { 
        Start-Dashboard -Rebuild $true
        exit 0
    }
    'stop' { 
        Stop-Dashboard
        exit 0
    }
    'restart' { 
        Restart-Dashboard
        exit 0
    }
    'logs' { 
        Show-Logs
        exit 0
    }
    'status' { 
        Show-Status
        Read-Host "Pressione Enter para continuar"
        exit 0
    }
    'cleanup' { 
        Remove-Dashboard
        exit 0
    }
}

# Menu interativo
while ($true) {
    Show-Menu
    $choice = Read-Host "Digite o numero da opcao"
    
    switch ($choice) {
        '1' { Start-Dashboard -Rebuild $true; Read-Host "`nPressione Enter para continuar" }
        '2' { Start-Dashboard -Rebuild $false; Read-Host "`nPressione Enter para continuar" }
        '3' { Stop-Dashboard; Read-Host "`nPressione Enter para continuar" }
        '4' { Show-Logs }
        '5' { Restart-Dashboard; Read-Host "`nPressione Enter para continuar" }
        '6' { Show-Status; Read-Host "`nPressione Enter para continuar" }
        '7' { Remove-Dashboard; Read-Host "`nPressione Enter para continuar" }
        '0' { 
            Write-Title "Obrigado por usar o Dashboard de Licenciamento Microsoft!"
            exit 0
        }
        default { Write-Warning-Custom "Opcao invalida! Tente novamente." }
    }
    
    Clear-Host
    Show-Banner
}
