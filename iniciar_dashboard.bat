@echo off
REM Script de Inicializacao Rapida do Dashboard
REM Licenciamento Microsoft - Docker Version

echo.
echo ================================================================================
echo       Dashboard de Licenciamento Microsoft - Inicializacao Docker
echo ================================================================================
echo.

REM Verificar se Docker esta instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Docker nao encontrado!
    echo.
    echo Por favor, instale o Docker Desktop:
    echo https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Docker Compose nao encontrado!
    echo.
    echo Por favor, certifique-se de que o Docker Desktop esta instalado corretamente.
    echo.
    pause
    exit /b 1
)

echo [OK] Docker e Docker Compose encontrados!
echo.

REM Verificar se o arquivo Excel existe
if not exist "LICENCIAMENTO MICROSOFT (1).xlsx" (
    echo [AVISO] Arquivo 'LICENCIAMENTO MICROSOFT (1).xlsx' nao encontrado!
    echo.
    echo Certifique-se de que o arquivo Excel esta neste diretorio:
    echo %CD%
    echo.
    pause
    exit /b 1
)

echo [OK] Planilha de dados encontrada!
echo.

REM Menu de opcoes
:menu
echo.
echo Escolha uma opcao:
echo.
echo  1 - Iniciar Dashboard (primeira vez / reconstruir)
echo  2 - Iniciar Dashboard (rapido - sem rebuild)
echo  3 - Parar Dashboard
echo  4 - Ver logs do Dashboard
echo  5 - Reiniciar Dashboard
echo  6 - Remover containers e volumes
echo  0 - Sair
echo.
set /p opcao="Digite o numero da opcao: "

if "%opcao%"=="1" goto build
if "%opcao%"=="2" goto start
if "%opcao%"=="3" goto stop
if "%opcao%"=="4" goto logs
if "%opcao%"=="5" goto restart
if "%opcao%"=="6" goto cleanup
if "%opcao%"=="0" goto end
goto menu

:build
echo.
echo ================================================================================
echo Construindo e iniciando o Dashboard...
echo Isso pode levar alguns minutos na primeira vez.
echo ================================================================================
echo.
docker-compose up -d --build
if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo Dashboard iniciado com sucesso!
    echo ================================================================================
    echo.
    echo Acesse em seu navegador: http://localhost:5000
    echo.
    echo Para ver os logs: execute este script novamente e escolha a opcao 4
    echo Para parar: execute este script novamente e escolha a opcao 3
    echo.
    echo ================================================================================
    timeout /t 3 >nul
    start http://localhost:5000
) else (
    echo.
    echo [ERRO] Falha ao iniciar o Dashboard.
    echo Verifique os logs acima para mais detalhes.
    echo.
)
pause
goto menu

:start
echo.
echo ================================================================================
echo Iniciando o Dashboard (modo rapido)...
echo ================================================================================
echo.
docker-compose up -d
if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo Dashboard iniciado com sucesso!
    echo ================================================================================
    echo.
    echo Acesse em seu navegador: http://localhost:5000
    echo.
    echo ================================================================================
    timeout /t 2 >nul
    start http://localhost:5000
) else (
    echo.
    echo [ERRO] Falha ao iniciar o Dashboard.
    echo.
)
pause
goto menu

:stop
echo.
echo ================================================================================
echo Parando o Dashboard...
echo ================================================================================
echo.
docker-compose stop
if %errorlevel% equ 0 (
    echo.
    echo [OK] Dashboard parado com sucesso!
) else (
    echo.
    echo [ERRO] Falha ao parar o Dashboard.
)
echo.
pause
goto menu

:logs
echo.
echo ================================================================================
echo Logs do Dashboard (Pressione Ctrl+C para sair)
echo ================================================================================
echo.
docker-compose logs -f
goto menu

:restart
echo.
echo ================================================================================
echo Reiniciando o Dashboard...
echo ================================================================================
echo.
docker-compose restart
if %errorlevel% equ 0 (
    echo.
    echo [OK] Dashboard reiniciado com sucesso!
    echo.
    echo Acesse em seu navegador: http://localhost:5000
    echo.
) else (
    echo.
    echo [ERRO] Falha ao reiniciar o Dashboard.
)
pause
goto menu

:cleanup
echo.
echo ================================================================================
echo ATENCAO: Isso vai remover todos os containers e volumes!
echo ================================================================================
echo.
set /p confirma="Tem certeza? (S/N): "
if /i "%confirma%"=="S" (
    echo.
    echo Removendo containers e volumes...
    docker-compose down -v
    if %errorlevel% equ 0 (
        echo.
        echo [OK] Limpeza concluida!
    ) else (
        echo.
        echo [ERRO] Falha na limpeza.
    )
) else (
    echo.
    echo Operacao cancelada.
)
echo.
pause
goto menu

:end
echo.
echo ================================================================================
echo Obrigado por usar o Dashboard de Licenciamento Microsoft!
echo ================================================================================
echo.
exit /b 0
