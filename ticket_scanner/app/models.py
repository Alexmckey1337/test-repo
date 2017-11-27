from config import db


# Models
class SummitAnket(db.Model):
    __table__ = db.Model.metadata.tables['summit_summitanket']

    def __repr__(self):
        return '%s' % self.id


class SummitAttend(db.Model):
    __table__ = db.Model.metadata.tables['summit_summitattend']

    def __repr__(self):
        return '%s' % self.id


class AnketStatus(db.Model):
    __table__ = db.Model.metadata.tables['summit_anketstatus']

    def __repr__(self):
        return '%s' % self.id


class AnketPasses(db.Model):
    __table__ = db.Model.metadata.tables['summit_anketpasses']

    def __repr__(self):
        return '%s' % self.id


class Summit(db.Model):
    __table__ = db.Model.metadata.tables['summit_summit']

    def __repr__(self):
        return '%s' % self.id


class SummitType(db.Model):
    __table__ = db.Model.metadata.tables['summit_summittype']

    def __repr__(self):
        return '%s' % self.title


class CustomUser(db.Model):
    __table__ = db.Model.metadata.tables['account_customuser']

    def __repr__(self):
        return '%s' % self.id


class User(db.Model):
    __table__ = db.Model.metadata.tables['auth_user']

    def __repr__(self):
        return '%s' % self.last_name


open_summits = db.session.query(Summit.id, SummitType.title).join(SummitType).filter(Summit.status == 'open').all()
