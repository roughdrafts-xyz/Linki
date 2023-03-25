import pytest

from sigili.title.repository import TitleDetails


# CAR needs to be able to track what the CAs are.
# CAR needs to provide CAs or information about them.

# Titles is the choice of phrase for current titles


def test_should_set_current_title():
    # titles only have one title, but one title can have multiple titles
    # should handle ignoring a no-op
    current_title_details = tmp_car.set_title(title, articleId)
    assert current_title_details == TitleDetails()

    # should handle a new set
    current_title_details = tmp_car.set_title(title, new_articleId)
    assert current_title_details == TitleDetails()

    # should unset a title
    current_title_details = tmp_car.set_title(title, None)
    assert current_title_details == None


def test_should_get_options():
    # return a list of titles with title
    options = tmp_car.get_options(title)
    assert options == [TitleDetails()]
    pass


def test_should_get_current_title():
    current_title_details = tmp_car.get_title(title)
    assert current_title_details == TitleDetails()
    pass


def test_should_list_current_titles():
    current_titles_details = tmp_car.get_titles()
    assert current_titles_details == [TitleDetails()]
    pass
