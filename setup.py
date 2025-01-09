import os
import shutil
import sys
import venv
import subprocess


def setup_virtualenv(env_dir: str, python_executable: str = sys.executable):
    """Creates a virtual environment."""
    if not os.path.exists(env_dir):
        venv.create(env_dir, with_pip=True, clear=True)
        print(f"Virtual environment created at {env_dir}.")
    else:
        print(f"Virtual environment already exists at {env_dir}.")

    activate_script = os.path.join(
        env_dir, "Scripts" if os.name == "nt" else "bin", "activate"
    )
    if not os.path.exists(activate_script):
        raise FileNotFoundError(f"Activation script not found at {activate_script}.")
    print(f"Activation script located at: {activate_script}")
    return activate_script


def install_requirements(env_dir: str, requirements_file: str):
    """Installs requirements from a requirements.txt file."""
    pip_path = os.path.join(env_dir, "Scripts" if os.name == "nt" else "bin", "pip")
    if not os.path.exists(pip_path):
        raise FileNotFoundError(f"Pip not found in virtual environment at {pip_path}.")

    if os.path.exists(requirements_file):
        subprocess.check_call([pip_path, "install", "-r", requirements_file])
        print(f"Installed requirements from {requirements_file}.")
    else:
        print(f"No requirements file found at {requirements_file}.")


def cleanup_virtualenv(env_dir: str):
    """Removes the virtual environment directory."""
    if os.path.exists(env_dir):
        shutil.rmtree(env_dir)
        print(f"Removed virtual environment at {env_dir}.")
    else:
        print(f"No virtual environment found at {env_dir} to remove.")


def main():
    env_dir = ".venv"
    requirements_file = "requirements.txt"

    while True:
        print("\nOptions:")
        print("1. Set up virtual environment")
        print("2. Install requirements")
        print("3. Clean up virtual environment")
        print("4. Exit")
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            setup_virtualenv(env_dir)
        elif choice == "2":
            install_requirements(env_dir, requirements_file)
        elif choice == "3":
            cleanup_virtualenv(env_dir)
        elif choice == "4":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please select a valid option.")


if __name__ == "__main__":
    main()
