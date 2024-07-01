import subprocess
import sys

def nvme_dsm_check(controller):

    command = ('sudo', 'nvme', 'dsm', controller, '-n', '1', '-b', '1', '-s', '0')
    print("---------------DSM Test----------------")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        matches = "success"
        print(result.stdout)
        if matches in result.stdout:
            print("Test Result: PASS\n")
            print("No error found during dsm test\n")
            return True
        else:
            print("Test Result: FAIL\n")
            return False
    else:
        print ("Error during command")
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
               print("Controlador não suportado.\n")
    return nvme_controllers, sata_controllers

def print_controller_info(controller):
    if controller.startswith('/dev/nvme'):
        nvme_dsm_check(controller)
        return True
    else:
        print("Controlador não suportado.\n")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Erro ao passar os argumentos. Uso: python script.py <nome_da_memoria>")
        sys.exit(1)
    
    partition_name = sys.argv[1]
    #partition_name = "nvme1n1"
    test_passed = test_storage(partition_name)
   


