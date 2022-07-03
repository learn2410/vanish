from random import randint

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from datacenter.models import Schoolkid, Mark, Chastisement, Lesson, Subject, Commendation


def fix_marks(schoolkid):
    bad_marks = Mark.objects.filter(schoolkid=schoolkid.id, points__in=[2, 3])
    count = bad_marks.count()
    bad_marks.update(points=5)
    print(f'-исправлено {count} плохих отметок')


def del_chastisments(schoolkid):
    chastisements = Chastisement.objects.filter(schoolkid=schoolkid.id)
    chastisements_quantity = chastisements.count()
    chastisements.delete()
    print(f'-удалено замечаний: {chastisements_quantity}')


def create_commendation(schoolkid, subject):
    used_dates = list(Commendation.objects.filter(
        schoolkid=schoolkid.id,
        subject=subject.id).values_list('created', flat=True))
    lessons = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter,
        subject=subject
    ).exclude(date__in=used_dates).order_by('-date')[0]
    commendations_count = Commendation.objects.count()
    text_commendation = Commendation.objects.all()[randint(0, commendations_count - 1)].text
    Commendation.objects.create(
        text=text_commendation,
        created=lessons.date,
        schoolkid=schoolkid,
        subject=lessons.subject,
        teacher=lessons.teacher)
    print(f'-добавлена похвала по предмету:"{subject.title}"')


def main():
    print('-------[ исправление электронного дневника ]-------')
    child_name = input('введите ФИО ученика:')
    try:
        schoolkid = Schoolkid.objects.get(full_name__contains=child_name)
    except ObjectDoesNotExist:
        print(f'Ошибка: ученик "{child_name}" не найден, уточните ФИО и повторите запрос')
        return
    except MultipleObjectsReturned:
        print(f'Ошибка:по запросу найдено несколько учеников, уточните и повторите запрос')
        return
    print(f'исправляем {schoolkid} id={schoolkid.id}')
    fix_marks(schoolkid)
    del_chastisments(schoolkid)
    subject_name = input('для добавления похвалы введите название предмета:')
    try:
        subject = Subject.objects.get(
            year_of_study=schoolkid.year_of_study,
            title__contains=subject_name)
    except (ObjectDoesNotExist, MultipleObjectsReturned) as ex:
        print(f'не верно указано название предмета"{subject_name}", похвалы не будет')
        return
    create_commendation(schoolkid, subject)


if __name__ == '__main__':
    main()
