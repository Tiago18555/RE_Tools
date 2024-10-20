import os

def read_binary_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            # Seek to the offset position
            file.seek(274)

            # Read the next 64 bytes
            data = file.read(64)

            # Convert bytes to integers
            values = [int(byte) for byte in data]

            return values
    except FileNotFoundError:
        print("Arquivo não encontrado.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None

def main():
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the file path for the .gs file in the same directory as the script
    file_path = os.path.join(script_dir, "arquivo.gsx")

    # Read the binary file
    values = read_binary_file(file_path)

    if values:
        print("Valores lidos a partir do offset 274 até os próximos 64 bytes:")
        print(values)

if __name__ == "__main__":
    main()