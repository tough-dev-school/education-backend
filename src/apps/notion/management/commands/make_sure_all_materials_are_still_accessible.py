import sys
from typing import Any

from django.core.management.base import BaseCommand

from apps.lms.models import Lesson
from apps.notion.models import Material, PageLink
from apps.notion.types import NotionId


def get_parent_ids(material: Material, tree: list[NotionId] | None = None) -> list[NotionId]:
    tree = tree if tree else list()

    parent_page_ids = PageLink.objects.filter(destination=material.page_id).values_list("source", flat=True)

    for parent in Material.objects.filter(page_id__in=parent_page_ids, course=material.course):
        if parent.page_id not in tree:
            tree.append(parent.page_id)
            tree += get_parent_ids(parent, tree)

    return list(dict.fromkeys(tree))


class Command(BaseCommand):
    help_text = "One-off command to check of all materials are still acessible after the lms app initial migration"

    def handle(self, *args: Any, **options: dict[str, Any]) -> None:
        linked_count = 0
        not_lined_count = 0
        materials_to_link = list()
        for material in Material.objects.iterator():
            self.stdout.write(f"Processing material {material.page_id}")

            parents = get_parent_ids(material)
            if len(parents) == 1 and parents[0] == material.page_id and not Lesson.objects.filter(material=material).exists():
                self.stdout.write(self.style.ERROR(f"Orphan material {material.id} {material}"))
                sys.exit(127)

            parent_is_found = False
            for parent in Material.objects.filter(page_id__in=get_parent_ids(material), course=material.course):
                if Lesson.objects.filter(material=parent).exists():
                    parent_is_found = True
                    linked_count + 1

            if parent_is_found:
                continue

            materials_to_link.append(material.id)

            self.stdout.write(
                self.style.ERROR(f"Material {material.title} from course {material.course.name} is not linked to lesson despite {len(parents)} parents")
            )
            not_lined_count += 1

        self.stdout.write(self.style.SUCCESS(f"{linked_count} materials linked to the lessons, {not_lined_count} are not linked"))

        materials_to_link_result = ", ".join([str(id) for id in materials_to_link])
        self.stdout.write(f"IDs of not-linked materials ({materials_to_link_result})")
