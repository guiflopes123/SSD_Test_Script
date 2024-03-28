# SSD Test Scripts

Este é um programa de interface gráfica simples em Python para executar testes em dispositivos NVMe e SATA. Ele permite selecionar os testes a serem executados e os dispositivos nos quais esses testes serão aplicados.

## Instalação

Para executar este programa, você precisará ter o Python 3 instalado em seu sistema. Além disso, certifique-se de ter instalado o pacote `tkinter`, que geralmente é incluído na instalação padrão do Python.

Para instalar o programa e suas dependências, siga estas etapas:

1. Clone este repositório para o seu sistema:

    ```
    git clone https://github.com/guiflopes123/SSD_Test_Script.git
    ```

2. Navegue até o diretório do projeto:

    ```
    cd SSD_Test_Script
    ```

3. Execute a instalação dos requisitos:

    ```
    ./install.sh
    ```
4. Executar o programa:

    ```
    sudo python3 Main_Interface.py 
    ```

Isso abrirá a interface gráfica do programa, onde você pode selecionar os testes a serem executados e os dispositivos em que deseja executá-los.

## Uso

Após iniciar o programa, você verá uma interface simples com opções para selecionar os testes e os dispositivos a serem testados. Selecione os testes desejados e os dispositivos nos quais deseja executá-los e clique no botão "Iniciar Teste". Os resultados dos testes serão exibidos na área de resultado da interface e o log com os dados coletados estão salvos dentro da pasta SSD_Test_Script.

