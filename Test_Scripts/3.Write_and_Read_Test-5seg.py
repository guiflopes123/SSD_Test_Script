import subprocess
import sys
import datetime
import os
import random
import time

def test_55(controller):
#----------------------Write and Compare Test 55-------------------------------
    if nvme_write(controller,start_block,num_blocks,block_size,pattern_01_file):
        if nvme_compare (controller,start_block,num_blocks,block_size,pattern_01_file):
            print("Write and Compare Test 55: PASS")
            nvme_format(controller)
            return True
        else:
            print ("55 Data comparison error!")
            return False
    else:
        print("Write and Compare Test 55: FAIL\n")
        return False

def sata_test_55(controller):
#----------------------Write and Compare Test 55-------------------------------
    if sata_write(controller,pattern_01_file):
        if sata_read (controller,pattern_01_file):
            print("Write and Compare Test 55: PASS")
            return True
        else:
            print ("55 Data comparison error!")
            return False
    else:
        print("Write and Compare Test 55: FAIL\n")
        return False

def sata_test_AA(controller):
#----------------------Write and Compare Test 55-------------------------------
    if sata_write(controller,pattern_10_file):
        if sata_read (controller,pattern_10_file):
            print("Write and Compare Test AA: PASS")
            return True
        else:
            print ("55 Data comparison error!")
            return False
    else:
        print("Write and Compare Test AA: FAIL\n")
        return False

def test_AA(controller):
#----------------------Write and Compare Test AA-------------------------------
    if nvme_write(controller,start_block,num_blocks,block_size,pattern_10_file):
        if nvme_compare (controller,start_block,num_blocks,block_size,pattern_10_file):
            print("Write and Compare Test AA: PASS")
            nvme_format(controller)
            return True
        else:
            print ("AA Data comparison error!")
            return False
    else:
        print("Write and Compare Test AA: FAIL\n")
        return False

#----------------------Check if both tests PASS-------------------------------


def nvme_format(controller):
   
    command = ('sudo', 'nvme', 'sanitize', controller, '-a', '2')
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print("NVME Format Done!")
        time.sleep(3)
        return True
    else:
        print ("Erro na formatação")
        return False

def nvme_compare(controller, start_block, num_blocks, block_size, input_file):

 # Construct the nvme compare command
    command = ['sudo', 'nvme', 'compare', controller, '-s', str(start_block), '-c', str(num_blocks), '-z', str(block_size),'-d', input_file]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        lines = str(result.stderr)
        if "compare: Success" in lines:
            # If the command succeeds, return True
            print("Compare command Success!")
            return True
        else:
            print("Compare command Failed!")
            return False
        
    else:
        # If the command fails, print the error and return False
        print(f"Error running command")
        return False

def sata_write(controller, input_file):
    try:
        with open(input_file, 'rb') as bin_file:
            bin_data = bin_file.read()
    except IOError as e:
        print("Erro ao ler o arquivo .bin:", e)
        return False
    try:
        with open(controller, 'wb') as f:
            f.write(bin_data)
        return True
    except IOError as e:
        print("Erro ao escrever na memória:", e)
        return False
    
def sata_read(controller, input_file):

    try:
        with open(input_file, 'rb') as bin_file:
            bin_data = bin_file.read()
            zero_data = bytes(len(bin_data))
            size = len(bin_data)
    except IOError as e:
        print("Erro ao ler o arquivo .bin:", e)
        return False
    try:
        with open(controller, 'rb') as f:
            data = f.read(size)
            if data == bin_data:
                with open(controller, 'wb') as f:
                    f.write(zero_data)
                return True
            else:
                with open(controller, 'wb') as f:
                    f.write(zero_data)
                return False
          

    except IOError as e:
        print("Erro ao ler na memória:", e)
        return False



def nvme_write(controller, start_block, num_blocks, block_size, input_file):

    # Construct the nvme write command
    #time.sleep(1)
    command = ['sudo', 'nvme', 'write', controller, '-s', str(start_block), '-c', str(num_blocks), '-z', str(block_size), '-d', input_file]
    #print(command)
    result = subprocess.run(command, capture_output=True, text=True)
    #print(result)
    if result.returncode == 0:
        lines = str(result.stderr)
       
        if "write: Success" in lines:
            print("Write Command: PASS\n")
            # If the command succeeds, return True
            return True
        else:
            return False
        
    else:
        # If the command fails, print the error and return False
        print("Error running command")

        return False

def generate_test_file(file_path, num_blocks, block_size, pattern):
    """
    Generate a test file with the specified pattern.

    Args:
        file_path (str): Path to the test file.
        num_blocks (int): Number of blocks to generate.
        block_size (int): Size of each block in bytes.
        pattern (str): Pattern to generate ('01', '10', 'random').

    Returns:
        None
    """
    with open(file_path, 'wb') as file:
        if pattern == '01':
            data = b'\x01\x00' * (block_size // 2)
        elif pattern == '10':
            data = b'\x00\x01' * (block_size // 2)
        elif pattern == 'random':
            data = bytes([random.randint(0, 1) for _ in range(block_size)])
        else:
            raise ValueError("Invalid pattern. Choose from '01', '10', or 'random'.")

        for _ in range(num_blocks):
            file.write(data)

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
               if controller not in sata_controllers:
                    sata_controllers.append(controller)
    return nvme_controllers, sata_controllers

def print_controller_info(controller):
    if controller.startswith('/dev/nvme'):
        if (test_55(controller) & test_AA(controller)):
            print("Test Result: PASS\n")
            return True
        else:
            print("Test Result: FAIL\n")
            return False
    elif controller.startswith('/dev/sd'):
        if (sata_test_55(controller) & sata_test_AA(controller)):
            print("Test Result: PASS\n")
            return True
        else:
            print("Test Result: FAIL\n")
            return False
    else:
        print("Controlador não suportado.\n")
        return False

start_block = 1
num_blocks = 10
block_size = 512  # You can adjust the block size as needed
base_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(base_dir, '..'))
pattern_01_file = parent_dir + '/test_pattern_01.bin'
pattern_10_file = parent_dir + '/test_pattern_10.bin'

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Erro ao passar os argumentos. Uso: python script.py <nome_da_memoria>")
        sys.exit(1)
    
    partition_name = sys.argv[1]
    #partition_name = "sdb"
    print("---------------Write and Compare Test----------------")
    test_passed = test_storage(partition_name)
   

    #generate_test_file(pattern_01_file, num_blocks, block_size, '01')
    #generate_test_file(pattern_10_file, num_blocks, block_size, '10')
    #print("Test files generated successfully.")
