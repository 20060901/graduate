

from ..utils.getPublicData import getAllJobs

def getAllTags():
    tagset=getAllJobs().values('companyTags')
    text=""
    for tags in tagset:
        if tags['companyTags'] !='无':
            for t in eval(tags['companyTags']):
                text += t+" "
    return text

def getAllNature():
    cnset=getAllJobs().values('companyNature')
    text=""
    for cns in cnset:
        for cn in cns['companyNature']:
            text += cn
    return text


