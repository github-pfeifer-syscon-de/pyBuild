#
# -*- coding: utf-8 -*-

from Job import Job

class Runner:
    jobs: list[Job]
    at: int
    def __init__(self,jobs: list[Job]):
        self.jobs = jobs
        self.at = 0

    def done(self):
        if self.at > 0:
            self.jobs[self.at-1].done()

    def next(self):
        if self.at < len(self.jobs):
            self.jobs[self.at].do()
            self.at += 1
