import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('test_hosts')


def test_paths(host):
    host_vars = host.ansible.get_variables()
    stage_items = host_vars['stage_items']

    for stage_item in stage_items:
        test_config = stage_item['_test_config']

        for path in test_config['paths']:
            print("Path: {0}".format(path))

            f = host.file(path)

            print("Path exists")
            assert f.exists
            print("Path is a file or directory")
            assert f.is_file or f.is_directory

            if f.is_file:
                print("File content")
                content = test_config['file_contents']
                assert f.content_string == content
                # modes are string representation of octal integers, so convert
                mode = int(test_config['mode'], 8)
                print("File mode")
                assert f.mode == mode
            else:
                print("Directory mode")
                # modes are string representation of octal integers, so convert
                directory_mode = int(test_config['directory_mode'], 8)
                assert f.mode == directory_mode

        if 'absent_paths' in test_config:
            for path in test_config['absent_paths']:
                print("Path: {0}".format(path))

                f = host.file(path)
                assert not f.exists
