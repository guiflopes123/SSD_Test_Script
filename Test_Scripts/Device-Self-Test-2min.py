import subprocess
import sys
import re
import time

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
        cmd = ['sudo', 'nvme', 'device-self-test', controller, '-n', '1', '-s', '1h']
        print("---------------Device-Self-Test----------------")
    else:
        print("Controlador não suportado.\n")
        return False

    controller_info = subprocess.run(cmd, capture_output=True, text=True)
    time.sleep(5)
    print(controller_info.stdout)
    if controller_info.returncode == 0:
        i=0
        while i==0:
            cmd = ['sudo', 'nvme', 'self-test-log', controller]
            response = subprocess.run(cmd, capture_output=True, text=True)
            lines = response.stdout.splitlines()
            current = lines[1]
            #print(current)
            if "0x1" in current:           
                i=0
                time.sleep(2)  
            else:
                operationresult = lines[4]
                print (operationresult)
                if "0" in operationresult:
                    print("Test Result: PASS\n")
                    print(lines[3])
                    print (lines[4])
                    i=1
                else:
                    print("Test Result: FAIL\n")
                    print(lines[3])
                    print (lines[4])

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
    test_passed = test_storage(partition_name)
