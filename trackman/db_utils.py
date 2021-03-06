from trackman import db
from trackman.models import DJ, Rotation, Track


def initdb():
    db.create_all()

    dj = DJ("Automation", "Automation", False)
    db.session.add(dj)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    # The first Rotation is always the default
    db.session.add(Rotation("None"))
    for r in ["Metal", "New Music", "Jazz", "Rock", "Americana"]:
        db.session.add(Rotation(r))

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


def add_sample_data():
    add_sample_djs()
    add_sample_tracks()


def add_sample_djs():
    db.session.add(DJ('Testy McTesterson', 'Testy McTesterson'))
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


def add_sample_tracks():
    db.session.add(Track('The Divine Conspiracy', 'Epica', 'The Divine Conspiracy', 'Avalon'))
    db.session.add(Track('Second Stone', 'Epica', 'The Quantum Enigma', 'Nuclear Blast'))
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise
