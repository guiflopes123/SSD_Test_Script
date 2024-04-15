import subprocess
import sys
import datetime
import os
import random

def get_nvme_device_path(partition_name):
    devices = []
    partitions_info = subprocess.run(['lsblk', '-d', '-n', '-o', 'NAME'], capture_output=True, text=True)
    partitions = partitions_info.stdout.splitlines()
    for partition in partitions:
        if partition.startswith(partition_name):
            device = "/dev/" + partition
            if device not in devices:
                devices.append(device)
    return devices

def write_data_to_nvme(device_path, data_size_mb):
    # Generating random data
    data = os.urandom(data_size_mb * 1024 * 1024)
    with open(device_path, 'wb') as nvme_device:
        nvme_device.write(data)

def read_data_from_nvme(device_path, data_size_mb):
    with open(device_path, 'rb') as nvme_device:
        data_read = nvme_device.read(data_size_mb * 1024 * 1024)
    return data_read

def test_nvme_memory(device_path, data_size_mb):
    # Escrever dados na NVMe
    write_data_to_nvme(device_path, data_size_mb)
    
    # Ler dados da NVMe
    data_read = read_data_from_nvme(device_path, data_size_mb)
    
    # Gerar dados aleatórios para comparar
    data_written = os.urandom(data_size_mb * 1024 * 1024)
    
    # Verificar se os dados lidos são os mesmos que os escritos
    if data_written == data_read:
        return True
    else:
        return False

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Erro ao passar os argumentos. Uso: python script.py <nome_da_memoria> <tamanho_dados_MB> <nome_arquivo_saida>")
        sys.exit(1)
    
    partition_name = sys.argv[1]
    data_size_mb = int(sys.argv[2])
    output_filename = sys.argv[3]

    nvme_devices = get_nvme_device_path(partition_name)

    if not nvme_devices:
        print("Nenhuma NVMe encontrada.")
        sys.exit(1)

    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    with open(output_filename, 'w') as logfile:
        for nvme_device in nvme_devices:
            logfile.write(f"Teste de Memória NVMe - {current_time}\n")
            logfile.write(f"Dispositivo NVMe: {nvme_device}\n")
            logfile.write(f"Tamanho dos Dados: {data_size_mb} MB\n")

            if test_nvme_memory(nvme_device, data_size_mb):
                logfile.write("Teste Resultado: PASS\n\n")
            else:
                logfile.write("Teste Resultado: FAIL\n\n")

    print("Teste concluído. Verifique o arquivo de log para detalhes.")
