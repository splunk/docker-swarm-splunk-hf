from __future__ import absolute_import

def default_or_present(value):
    if "state" not in value or value["state"]=="present":
        return True

    return False

def defined_absent(value):
    if "state" in value and value["state"]=="absent":
        return True

    return False


class TestModule(object):

    def tests(self):
        return {
            'default_or_present': default_or_present,
            'defined_absent': defined_absent,
        }
