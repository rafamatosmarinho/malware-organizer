import os
import shutil
import zipfile

# Caminho base para o diretório que contém as pastas com os arquivos
base_dir = "/home/kali/Downloads/theZoo-master/malware/Binaries/"

# Caminho para a pasta onde os arquivos serão copiados
output_dir = "/home/kali/Downloads/theZoo-master/malware/malware_all"

# Senha para extrair arquivos ZIP
zip_password = b"infected"

# Contador de arquivos movidos
files_moved_count = 0


def clear_output_dir():
    """
    Limpa o diretório de saída (output_dir), removendo todos os arquivos e subdiretórios.
    Se o diretório não existir, ele será criado.
    """
    if os.path.exists(output_dir):
        for file_name in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file_name)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Erro ao deletar {file_path}: {e}")
    else:
        os.makedirs(output_dir)


def is_target_file(file_path, extensions):
    """
    Verifica se um arquivo possui uma das extensões desejadas.

    Args:
        file_path (str): Caminho completo do arquivo.
        extensions (list): Lista de extensões desejadas.

    Returns:
        bool: True se o arquivo tiver uma das extensões, False caso contrário.
    """
    if not extensions:  # Se nenhuma extensão for informada, copia todos os arquivos
        return True
    return any(file_path.endswith(ext) for ext in extensions)


def copy_target_files(source_dir, extensions):
    """
    Copia arquivos com as extensões desejadas para o diretório de saída.

    Args:
        source_dir (str): Diretório de origem dos arquivos.
        extensions (list): Lista de extensões desejadas.

    Returns:
        bool: True se pelo menos um arquivo foi copiado, False caso contrário.
    """
    global files_moved_count
    files_found = False  # Flag para verificar se arquivos foram encontrados
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if is_target_file(file_path, extensions):
                shutil.copy(file_path, output_dir)
                print(f"Copiado: {file_path} -> {output_dir}")
                files_moved_count += 1
                files_found = True
    return files_found


def extract_zip(zip_path, extract_dir):
    """
    Extrai arquivos de um ZIP protegido por senha.

    Args:
        zip_path (str): Caminho completo do arquivo ZIP.
        extract_dir (str): Diretório onde os arquivos serão extraídos.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_files = zip_ref.namelist()
            for file in zip_files:
                if os.path.basename(file).startswith('.'):  # Ignora arquivos ocultos
                    print(f"Ignorando arquivo oculto: {file}")
                    continue
                try:
                    zip_ref.extract(file, extract_dir, pwd=zip_password)
                    print(f"Extraído: {file} -> {extract_dir}")
                except RuntimeError as e:
                    if "compression method" in str(e):
                        print(
                            f"Erro: Método de compressão não suportado para {file}")
                    else:
                        print(f"Erro ao extrair {file}: {e}")
    except zipfile.BadZipFile:
        print(f"Erro: {zip_path} não é um arquivo ZIP válido.")
    except Exception as e:
        print(f"Erro ao processar {zip_path}: {e}")


def process_directory(directory, extensions):
    """
    Processa uma pasta específica, copiando arquivos com as extensões desejadas
    e extraindo arquivos ZIP.

    Args:
        directory (str): Caminho da pasta a ser processada.
        extensions (list): Lista de extensões desejadas.

    Returns:
        bool: True se pelo menos um arquivo foi processado, False caso contrário.
    """
    global files_moved_count  # Declara que estamos usando a variável global

    if not os.path.exists(directory):
        print(f"A pasta {directory} não foi encontrada.")
        return False

    files_found = False  # Flag para verificar se arquivos foram encontrados
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            if file.endswith(".zip"):  # Processa arquivos ZIP
                temp_dir = os.path.join(root, "temp_extracted")
                os.makedirs(temp_dir, exist_ok=True)
                extract_zip(file_path, temp_dir)
                if copy_target_files(temp_dir, extensions):
                    files_found = True
                shutil.rmtree(temp_dir)  # Remove o diretório temporário

            # Copia arquivos com extensões desejadas
            elif is_target_file(file_path, extensions):
                shutil.copy(file_path, output_dir)
                print(f"Copiado: {file_path} -> {output_dir}")
                files_moved_count += 1
                files_found = True

    return files_found


# Pede ao usuário para digitar as extensões desejadas (opcional)
extensions_input = input(
    "Digite as extensões desejadas (separadas por vírgula, ou deixe em branco para todas): ").strip()
extensions = [ext.strip() for ext in extensions_input.split(",")
              ] if extensions_input else []

# Pede ao usuário para digitar as pastas desejadas (opcional)
directories_input = input(
    "Digite as pastas desejadas (separadas por vírgula, ou deixe em branco para a pasta padrão): ").strip()
directories = [os.path.join(base_dir, dir.strip()) for dir in directories_input.split(
    ",")] if directories_input else [base_dir]

# Limpa a pasta malware_all antes de começar
clear_output_dir()

# Processa cada pasta informada pelo usuário
for directory in directories:
    if not process_directory(directory, extensions):
        if extensions:
            print(
                f"Não foram encontrados arquivos com as extensões {', '.join(extensions)} na pasta {directory}.")
        else:
            print(f"Não foram encontrados arquivos na pasta {directory}.")

# Verifica a quantidade real de arquivos na pasta malware_all
actual_files_count = len([name for name in os.listdir(
    output_dir) if os.path.isfile(os.path.join(output_dir, name))])

# Exibe o total de arquivos movidos e a quantidade real na pasta
print(f"\nTotal de arquivos movidos para {output_dir}: {files_moved_count}")
print(f"Quantidade real de arquivos em {output_dir}: {actual_files_count}")

# Verifica se a contagem está correta
if files_moved_count != actual_files_count:
    print("Atenção: A contagem de arquivos movidos não corresponde à quantidade real na pasta.")
