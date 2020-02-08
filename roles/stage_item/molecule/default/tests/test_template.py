import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_basic_template(host):
    host_vars = host.ansible.get_variables()
    test_vars = host_vars['_test_config']

    templated_content = test_vars['templated_file_contents']

    # modes are string representations of octal integers, so convert them
    templated_directory_mode = int(test_vars['directory_mode'], 8)
    templated_file_mode = int(test_vars['file_mode'], 8)

    templated_paths = test_vars['templated_paths']

    print("testing host: {0}".format(host_vars['inventory_hostname']))
    for templated_path in templated_paths:
        print("Path: {0}".format(templated_path))

        f = host.file(templated_path)

        print("Path exists")
        assert f.exists
        print("Path is a file or directory")
        assert f.is_file or f.is_directory

        if f.is_file:
            print("Templated file content")
            assert f.content_string == templated_content
            print("Templated file mode")
            assert f.mode == templated_file_mode
        else:
            print("Templated directory mode")
            assert f.mode == templated_directory_mode
