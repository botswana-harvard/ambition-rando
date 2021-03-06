import csv
import os
import sys

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style
from tqdm import tqdm

from .constants import SINGLE_DOSE
from .utils import get_drug_assignment
from .models import RandomizationList

style = color_style()


class RandomizationListImportError(Exception):
    pass


def import_randomization_list(path=None, verbose=None, overwrite=None, add=None):
    """Imports CSV.

    Format:
        sid,drug_assignment,site_name, orig_site, orig_allocation, orig_desc
        1,single_dose,gaborone
        2,two_doses,gaborone
        ...
    """

    verbose = True if verbose is None else verbose
    path = path or os.path.join(settings.RANDOMIZATION_LIST_PATH)
    path = os.path.expanduser(path)
    if overwrite:
        RandomizationList.objects.all().delete()
    if RandomizationList.objects.all().count() > 0 and not add:
        raise RandomizationListImportError(
            'Not importing CSV. RandomizationList model is not empty!')
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        sids = [row['sid'] for row in reader]
    if len(sids) != len(list(set(sids))):
        raise RandomizationListImportError(
            'Invalid file. Detected duplicate SIDs')
    sid_count = len(sids)
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in tqdm(reader, total=sid_count):
            row = {k: v.strip() for k, v in row.items()}
            try:
                RandomizationList.objects.get(sid=row['sid'])
            except ObjectDoesNotExist:

                drug_assignment = get_drug_assignment(row)

                try:
                    allocation = row['orig_allocation']
                except KeyError:
                    allocation = '2' if drug_assignment == SINGLE_DOSE else '1'

                RandomizationList.objects.create(
                    sid=row['sid'],
                    drug_assignment=drug_assignment,
                    site_name=row['site_name'],
                    allocation=allocation)
    count = RandomizationList.objects.all().count()
    if verbose:
        sys.stdout.write(style.SUCCESS(
            f'(*) Imported {count} SIDs from {path}.\n'))
