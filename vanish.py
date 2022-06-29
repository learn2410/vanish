from random import randint

from datacenter.models import Schoolkid, Mark, Chastisement, Lesson, Subject, Commendation


def get_schoolkid(fio='Фролов Иван'):
    query = Schoolkid.objects.filter(full_name__contains=fio)
    found_quantity = len(query)
    if found_quantity == 1:
        return query[0]
    else:
        print(f'Ошибка: найдено учеников:{found_quantity}, уточните ФИО и повторите запрос')
        exit(1)


def fix_marks(child_name):
    schoolkid = get_schoolkid(child_name)
    bad_marks = Mark.objects.filter(schoolkid=schoolkid.id, points__in=[2, 3])
    count = bad_marks.count()
    bad_marks.update(points=5)
    print(f'-исправлено {count} плохих отметок')


def del_castisment(child_name):
    schoolkid = get_schoolkid(child_name)
    chastisements = Chastisement.objects.filter(schoolkid=schoolkid.id)
    chastisements_quantity = chastisements.count()
    chastisements.delete()
    print(f'-удалено замечаний: {chastisements_quantity}')


def create_commendation(child_name, subject_name='(не указан)'):
    schoolkid = get_schoolkid(child_name)
    subjects = Subject.objects.filter(
        year_of_study=schoolkid.year_of_study,
        title__contains=subject_name)
    if len(subject_name) == 0 or len(subjects) == 0:
        print(f'--не найден предмет:"{subject_name}", похвалы не будет')
        return
    subject = subjects[0]
    subject_name = subject.title
    used_dates = list(Commendation.objects.filter(
        schoolkid=schoolkid.id,
        subject=subject).values_list('created', flat=True))
    lessons = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter,
        subject=subject
    ).exclude(date__in=used_dates).order_by('-date')[0]
    count_commendations = Commendation.objects.count()
    text_commendation = Commendation.objects.all()[randint(0, count_commendations - 1)].text
    Commendation.objects.create(
        text=text_commendation,
        created=lessons.date,
        schoolkid=schoolkid,
        subject=lessons.subject,
        teacher=lessons.teacher)
    print(f'-добавлена похвала по предмету:"{subject.title}"')


print('-------[ исправление электронного дневника ]-------')
child_name = input('введите ФИО ученика:')
schoolkid = get_schoolkid(child_name)
print(f'исправляем {schoolkid} id={schoolkid.id}')
fix_marks(child_name)
del_castisment(child_name)
subject = input('для добавления похвалы введите название предмета:')
create_commendation(child_name, subject)
