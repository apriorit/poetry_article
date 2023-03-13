import glob
import logging
import os
import shutil
import subprocess
import pkg_resources

EXCLUDE_PROJECTS = ['Deploy', 'venv']
CMD_CREATE_WHEEL = '{0} {1} bdist_wheel -d {2}'
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
OUTPUT_ARTIFACTS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'artifacts'))
OUTPUT_BUILD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build'))

PRIVATE_PACKAGES = {}
DEPENDENCIES = {}


def run_command(command, working_dir=None):
    # print("Running shell command: {0}".format(command))
    if working_dir:
        process = subprocess.check_output(command, cwd=working_dir, shell=True)
    else:
        process = subprocess.check_output(command, shell=True)
    return process


def add_private_packages(package_name, wheel_name, requirement_path, apt_path):
    PRIVATE_PACKAGES[package_name] = {"whl": os.path.join(OUTPUT_ARTIFACTS, wheel_name),
                                      "requirement": requirement_path,
                                      "python_version": 'python3',
                                      "apt_path": apt_path}


def get_package_name(setup_path):
    dir_path = os.path.abspath(os.path.join(setup_path, os.pardir))
    return str(run_command(f'python3 {setup_path} --name', dir_path), encoding='utf-8').replace('\n', '')


def build_wheel(setup_path):
    dir_path = os.path.abspath(os.path.join(setup_path, os.pardir))
    create_wheel_command = CMD_CREATE_WHEEL.format('python3', setup_path, OUTPUT_ARTIFACTS)
    run_command(create_wheel_command, dir_path)



def copy_wheel(package_name, dest):
    if package_name in PRIVATE_PACKAGES:
        path = PRIVATE_PACKAGES[package_name]["whl"]
        for file in glob.glob(path):
            shutil.copy(file, dest)
    else:
        logging.info(f'missing {package_name}')


def copy_apt(apt_path, dest):
    if os.path.exists(apt_path):
        shutil.copy(apt_path, dest)


def copy_additional_packages(additional_packages, dest):
    if os.path.exists(additional_packages):
        if not os.path.exists(dest):
            os.makedirs(dest, exist_ok=True)
        for file in glob.glob(os.path.join(additional_packages, '*.*')):
            shutil.copy(file, dest)


def copy_additional_files(additional_files, dest):
    if os.path.exists(additional_files):
        if not os.path.exists(dest):
            os.makedirs(dest, exist_ok=True)
        for file in glob.glob(os.path.join(additional_files, '*.*')):
            shutil.copy(file, dest)


def clean_up_spaces(requirement_dest):
    # there is cases where the requirement file has empty lines - this fuc removes it
    tmp_file_name = requirement_dest + 'tmp'
    with open(requirement_dest, 'r', encoding='utf-8') as inFile, \
            open(requirement_dest + 'tmp', 'w', encoding='utf-8') as outFile:
        for line in inFile:
            if line.strip():
                outFile.write(line)
    os.remove(requirement_dest)
    os.rename(tmp_file_name, requirement_dest)


def copy_requirement_data(package_name, requirement_dest):
    # copy from the requirement file to the dependencies requirement file
    requirement_path_to_add = PRIVATE_PACKAGES[package_name]["requirement"]
    package_name = PRIVATE_PACKAGES[package_name]["whl"]

    if os.path.exists(requirement_path_to_add):
        requirement_data_to_add = open(requirement_path_to_add).read()

        if os.stat(requirement_path_to_add).st_size > 0:
            with open(requirement_dest, "a") as myfile:
                myfile.write('\n')
                myfile.write('#' + os.path.basename(package_name) + '\n')
                myfile.writelines(requirement_data_to_add)
        clean_up_spaces(requirement_dest)


def find_private_package_fuzzy_matching(expected_package_name):
    if expected_package_name.replace('_', '-') in [whl for whl in PRIVATE_PACKAGES]:
        return expected_package_name.replace('_', '-')
    if expected_package_name.replace('-', '_') in [whl for whl in PRIVATE_PACKAGES]:
        return expected_package_name.replace('-', '_')
    return None


def find_all_dependencies_for_package(package_name, list_of_dependencies=None):
    if list_of_dependencies is None:
        list_of_dependencies = []

    # if packages has no dependencies or package not in the dependencies list -> return the list
    if package_name not in DEPENDENCIES or len(DEPENDENCIES[package_name]) == 0:
        return list(dict.fromkeys(list_of_dependencies))

    # get list of dependencies
    list_of_dependencies_for_this_package = DEPENDENCIES[package_name]
    for package in list_of_dependencies_for_this_package:
        if package not in list_of_dependencies:
            list_of_dependencies.append(package)
            # call again in recursion
            find_all_dependencies_for_package(package, list_of_dependencies)
    return list_of_dependencies


def build_internal_wheels():
    logging.info("BUILD INTERNAL WHEELS START")
    for subdir, dirs, files in os.walk(ROOT_PATH):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_PROJECTS]
        for file in files:
            if file == 'setup.py':
                try:
                    full_setup_path = os.path.join(subdir, file)
                    build_wheel(setup_path=full_setup_path)
                    requirement_dest_path = full_setup_path.replace("setup.py", "requirements.txt")
                    apt_dest_path = full_setup_path.replace("setup.py", "apt.txt")
                    if not os.path.exists(apt_dest_path):
                        apt_dest_path = None
                    name = get_package_name(setup_path=full_setup_path)
                    whl_name = f'{name}-*.whl'

                    add_private_packages(name, whl_name, requirement_dest_path, apt_dest_path)
                    logging.info(f'Wheels created: {name}')
                except:
                    pass

    logging.info("BUILD INTERNAL WHEELS END")


def create_deploy_folders():
    logging.info("CREATING DEPLOY BUILD START")
    for subdir, dirs, files in os.walk(ROOT_PATH):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_PROJECTS]
        for file in files:
            if file == 'requirements.txt':
                try:
                    setup_path = os.path.join(subdir, 'setup.py')

                    apt_path = os.path.join(subdir, 'apt.txt')
                    additional_packages = os.path.join(subdir, 'additional_packages')
                    additional_files = os.path.join(subdir, 'additional_files')
                    package_name = get_package_name(setup_path)

                    full_requirements_path = os.path.join(subdir, file)

                    dest_wheels = os.path.join(OUTPUT_BUILD, package_name, "wheels")
                    # create dest deploy folder for wheels
                    os.makedirs(dest_wheels, exist_ok=True)

                    # copy itself
                    copy_wheel(package_name, dest_wheels)

                    # copy apt file
                    copy_apt(apt_path, os.path.join(OUTPUT_BUILD, package_name))

                    copy_additional_packages(additional_packages, os.path.join(OUTPUT_BUILD, package_name, 'additional_packages'))
                    copy_additional_files(additional_files, os.path.join(OUTPUT_BUILD, package_name, 'additional_files'))

                    if package_name not in DEPENDENCIES:
                        DEPENDENCIES[package_name] = []
                    with open(full_requirements_path) as dependencies:
                        for req in pkg_resources.parse_requirements(dependencies):
                            dependency_name = find_private_package_fuzzy_matching(req.name)
                            if dependency_name:
                                copy_wheel(dependency_name, dest_wheels)
                                DEPENDENCIES[package_name].append(dependency_name)

                    # copy requirements
                    dest_requirement = os.path.join(OUTPUT_BUILD, package_name, 'requirements.txt')
                    shutil.copy(full_requirements_path, dest_requirement)

                    logging.info(f'Added to deploy build: {package_name}')

                except:
                    pass

    logging.info("CREATING DEPLOY BUILD END")


def copy_apt_data(package_name, dest):
    # copy from the apt file to the dependencies apt file
    apt_path_to_add = PRIVATE_PACKAGES[package_name]["apt_path"]
    if apt_path_to_add:
        if os.path.exists(apt_path_to_add):
            apt_data_to_add = open(apt_path_to_add).readlines()

            if os.path.exists(dest):
                append_write = 'a'  # append if already exists
            else:
                append_write = 'w'  # make a new file if not
            if os.stat(apt_path_to_add).st_size > 0:
                with open(dest, append_write) as myfile:
                    myfile.write('\n')
                    myfile.write("".join(apt_data_to_add))


def add_dependencies_wheels_and_requirements():
    logging.info("ADDING DEPENDENCIES START")
    for subdir, dirs, files in os.walk(ROOT_PATH):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_PROJECTS]
        for file in files:
            if file == 'setup.py':
                try:
                    setup_file_path = os.path.join(subdir, file)

                    name = get_package_name(setup_file_path)

                    dest_wheels = os.path.join(OUTPUT_BUILD, name, "wheels")
                    dest_apt = os.path.join(OUTPUT_BUILD, name, "apt.txt")
                    to_add = find_all_dependencies_for_package(name)
                    logging.info(f'\nPackage: {name}'
                                 f'\nDependencies: {to_add}')

                    if to_add:
                        for package in to_add:
                            copy_wheel(package, dest_wheels)

                            # append requirements
                            dest_requirement = os.path.join(OUTPUT_BUILD, name, 'requirements.txt')
                            copy_requirement_data(package, dest_requirement)
                except:
                    pass

    logging.info("ADDING DEPENDENCIES END")


def cleanup():
    logging.info("CLEANUP START")
    for subdir, dirs, files in os.walk(OUTPUT_BUILD):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_PROJECTS]
        for dir in dirs:
            wheels_3 = os.path.join(subdir, dir, 'wheels')

            if os.path.exists(wheels_3):
                for file in glob.glob(os.path.join(wheels_3, '*.*')):
                    if 'py2' in file:
                        os.remove(file)

            if dir.endswith('egg-info') or dir == 'build':
                logging.info(f'Removing {os.path.join(subdir, dir)}')
                shutil.rmtree(os.path.join(subdir, dir))

    for subdir, dirs, files in os.walk(ROOT_PATH):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_PROJECTS]
        for dir in dirs:

            if dir.endswith('egg-info') or dir == 'build':
                logging.info(f'Removing: {os.path.join(subdir, dir)}')
                shutil.rmtree(os.path.join(subdir, dir))

    logging.info("CLEANUP END")


def main():
    def init_logs():
        logger = logging.getLogger()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        ch.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
        logger.addHandler(ch)

    init_logs()

    try:
        # build all private wheels
        build_internal_wheels()

        # create artifacts
        create_deploy_folders()

        # add all dependencies
        add_dependencies_wheels_and_requirements()

        # remove all egg-info and build folders
        cleanup()

    except Exception as e:
        logging.exception('Failed to build wheels')


if __name__ == '__main__':
    main()
