import subprocess
import sys
import re

def get_nvme_controllers(partition_name):
    nvme_controllers = []
    sata_controllers = []
    partitions_info = subprocess.run(['lsblk', '-d', '-n', '-o', 'NAME'], capture_output=True, text=True)
    partitions = partitions_info.stdout.splitlines()
    for partition in partitions:
        if partition.startswith(partition_name):
            controller = "/dev/" + partition
            if controller.startswith('/dev/nvme'):
                if controller not in nvme_controllers:
                    nvme_controllers.append(controller)
            elif controller.startswith('/dev/sd'):
                if controller not in sata_controllers:
                    sata_controllers.append(controller)
    return nvme_controllers, sata_controllers

def print_controller_info(controller):
    if controller.startswith('/dev/nvme'):
        cmd = ['sudo', 'nvme', 'smart-log', controller]
        print("---------------SMART LOG Test----------------")
        controller_info = subprocess.run(cmd, capture_output=True, text=True)
        if controller_info.returncode == 0:
            pattern = r"critical_warning.*"
                    # Procura todas as linhas que correspondem ao padrão
            matches = re.findall(pattern, controller_info.stdout)
        #print(matches)
        # Se encontrou alguma correspondência
            if matches:
            # Itera sobre todas as correspondências
                for match in matches:
            # Se o status do teste for PASS, então o teste passou
                    if "0" in match:
                        print("Test Result: PASS\n")
                        print(controller_info.stdout)
                        break
                # Se o status do teste for FAIL, então o teste falhou
                    else:
                        print("Test Result: FAIL\n")
                        break
    elif('/dev/sd'):
        cmd = ['sudo', 'skdump', controller]
        #print(cmd)
        print("---------------SMART LOG Test----------------")
        controller_info = subprocess.run(cmd, capture_output=True, text=True)
        if controller_info.returncode == 0:
            pattern = r"SMART Disk Health Good: yes"
                    # Procura todas as linhas que correspondem ao padrão
            matches = re.findall(pattern, controller_info.stdout)
        #print(matches)
        # Se encontrou alguma correspondência
            if matches:
            # Itera sobre todas as correspondências
                for match in matches:
            # Se o status do teste for PASS, então o teste passou
                    if "yes" in match:
                        print("Test Result: PASS\n")
                        print(controller_info.stdout)
                        break
                # Se o status do teste for FAIL, então o teste falhou
                    else:
                        print("Test Result: FAIL\n")
                        break
    else:
        print("Test Result: FAIL\n")
        return False

def test_storage(partition_name):
    nvme_controllers, sata_controllers = get_nvme_controllers(partition_name)
    if nvme_controllers or sata_controllers:
            for controller in nvme_controllers:
                if not print_controller_info(controller):
                    return False
            for controller in sata_controllers:
                if not print_controller_info(controller):
                    return False
            return True
    else:
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Erro ao passar os argumentos")
        sys.exit(1)
    
    partition_name = sys.argv[1]
    #partition_name = "sda"
    test_passed = test_storage(partition_name)
