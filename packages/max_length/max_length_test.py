from yaplint_core import linter

from yaplint_max_length import MaxLength


def test_max_length_good():
    src = "print('this line is less than 80 characters')"
    rules = [MaxLength()]
    actual = linter(src, rules)
    expected = []
    assert actual["errors"] == expected


def test_max_length_setting_good():
    src = "print('this line is less than 100 characters, but i need to really stretch it. who knows.')"
    rules = [MaxLength({"code": 100})]
    actual = linter(src, rules)
    expected = []
    assert actual["errors"] == expected


def test_max_length_error():
    src = "print('this line is less than 100 characters, but i need to really stretch it. who knows.')"
    rules = [MaxLength()]
    actual = linter(src, rules)
    expected = [{
        "filename": "",
        "lineno": 1,
        "msg": "max line has been exceeded 91 > 80",
        "name": "max_length",
    }]
    assert actual["errors"] == expected
