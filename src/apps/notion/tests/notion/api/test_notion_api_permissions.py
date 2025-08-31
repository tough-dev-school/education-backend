import pytest
from django.db.models import Q

from apps.notion.models import Material

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("mock_notion_response"),
]


def test_no_anon(anon):
    anon.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/", expected_status_code=401)


@pytest.mark.usefixtures("unpaid_order")
@pytest.mark.parametrize(
    "material_slug",  # this is actualy the same material. 0e5693d2173a4f77ae8106813b6e5329 is notion page_id, 4d5726e8ee524448b8f97be4c7f8e632 is our internal slug
    [
        "0e5693d2173a4f77ae8106813b6e5329",
        "4d5726e8ee524448b8f97be4c7f8e632",
    ],
)
def test_404_for_not_purchased_materials(api, mock_notion_response, material_slug):
    assert Material.objects.filter(Q(slug=material_slug) | Q(page_id=material_slug)).exists(), "Make sure material actualy exists before checking for 404"

    api.get(f"/api/v2/materials/{material_slug}/", expected_status_code=404)

    mock_notion_response.assert_not_called()


def test_ok_for_materials_with_same_page_id_from_another_course(api, mixer, another_course):
    material_from_another_course_with_same_page_id = mixer.blend(
        "notion.Material",
        course=another_course,
        page_id="0e5693d2173a4f77ae8106813b6e5329",
        slug="b6e7820540cf4cb8b55875ae533dd298",
    )

    api.get(
        path=f"/api/v2/materials/{material_from_another_course_with_same_page_id.slug}/",
        expected_status_code=200,
    )


def test_ok_for_related_materials(api, mixer, another_course):
    """Make a relation from the purchased material to the non-purchased and check if user can see it"""
    material_from_another_course = mixer.blend("notion.Material", course=another_course)
    mixer.blend("notion.PageLink", source="0e5693d2173a4f77ae8106813b6e5329", destination=material_from_another_course.page_id)

    api.get(
        path=f"/api/v2/materials/{material_from_another_course.slug}/",
        expected_status_code=200,
    )


def test_second_level_of_relation(api, mixer, another_course):
    """Same as above but with 2 levels"""
    first_level = mixer.blend("notion.Material", course=another_course)
    second_level = mixer.blend("notion.Material", course=another_course)

    mixer.blend("notion.PageLink", source="0e5693d2173a4f77ae8106813b6e5329", destination=first_level.page_id)
    mixer.blend("notion.PageLink", source=first_level.page_id, destination=second_level.page_id)

    api.get(
        path=f"/api/v2/materials/{second_level.slug}/",
        expected_status_code=200,
    )


def test_third_level_of_relation(api, mixer, another_course):
    """Same as above but with 3 levels"""
    first_level = mixer.blend("notion.Material", course=another_course)
    second_level = mixer.blend("notion.Material", course=another_course)
    third_level = mixer.blend("notion.Material", course=another_course)

    mixer.blend("notion.PageLink", source="0e5693d2173a4f77ae8106813b6e5329", destination=first_level.page_id)
    mixer.blend("notion.PageLink", source=first_level.page_id, destination=second_level.page_id)
    mixer.blend("notion.PageLink", source=second_level.page_id, destination=third_level.page_id)

    api.get(
        path=f"/api/v2/materials/{third_level.slug}/",
        expected_status_code=200,
    )


def test_recursive_relation(api, mixer, another_course):
    """Create materials that link each other and check if all of them are accessible"""
    first_level = mixer.blend("notion.Material", course=another_course)
    second_level = mixer.blend("notion.Material", course=another_course)

    mixer.blend("notion.PageLink", source="0e5693d2173a4f77ae8106813b6e5329", destination=first_level.page_id)
    mixer.blend("notion.PageLink", source=first_level.page_id, destination="0e5693d2173a4f77ae8106813b6e5329")

    mixer.blend("notion.PageLink", source=first_level.page_id, destination=second_level.page_id)
    mixer.blend("notion.PageLink", source=second_level.page_id, destination=first_level.page_id)

    mixer.blend("notion.PageLink", source=second_level.page_id, destination="0e5693d2173a4f77ae8106813b6e5329")  # back to the top level

    for slug in ["0e5693d2173a4f77ae8106813b6e5329", first_level.slug, second_level.slug]:
        api.get(
            path=f"/api/v2/materials/{slug}/",
            expected_status_code=200,
        )


@pytest.mark.usefixtures("unpaid_order")
def test_ok_for_superuser(api):
    api.user.update(is_superuser=True)

    api.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/", expected_status_code=200)


@pytest.mark.usefixtures("unpaid_order")
def test_ok_for_user_with_permissions(api):
    api.user.add_perm("notion.material.see_all_materials")

    api.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/", expected_status_code=200)  # fetching material (its is an autoused fixture)


@pytest.mark.usefixtures("unpaid_order")
def test_superusers_do_not_fail_when_two_materials_with_the_same_id_are_present(api, mixer):
    api.user.add_perm("notion.material.see_all_materials")
    mixer.cycle(2).blend("notion.Material", page_id="0e5693d2173a4f77ae8106813b6e5329")

    api.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/", expected_status_code=200)


def test_sql_does_not_fail_for_users_that_purchased_two_courses(api, factory, another_course):
    """Test for a bug in the raw SQL, glitchtip id EDUCATION-BACKEND-8R"""
    factory.order(user=api.user, item=another_course, is_paid=True)

    api.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/", expected_status_code=200)  # fetching material (its is an autoused fixture)


def test_users_that_purchased_to_courses_have_access_to_both_materials(api, factory, another_course, mixer, material):
    """Continuing the previous test to make sure users that purchased two or more courses have access to their materials"""
    factory.order(user=api.user, item=another_course, is_paid=True)
    another_material = mixer.blend("notion.Material", course=another_course)

    api.get(f"/api/v2/materials/{material.slug}/", expected_status_code=200)  # material from the course purchased in fixtures
    api.get(f"/api/v2/materials/{another_material.slug}/", expected_status_code=200)  # material from the course purchased here
