# coding: utf8

from __future__ import print_function
import os
import sys
import argparse
import json

try:
    from urllib.request import urlopen, HTTPError
except ImportError:
    from urllib2 import urlopen, HTTPError


def print_ok(text):
    print(u"\u2713 {}".format(text))


def print_no(text):
    print(u"\u2718 {}".format(text))


def get_build_spec(build_spec_path):
    with open(build_spec_path) as f:
        return json.load(f)


def main(org, project, commit):
    url_target = "https://raw.githubusercontent.com/{org}/{project}/{commit}/setup.py".format(
        org=org, project=project, commit=commit
    )
    try:
        with urlopen(url_target) as req:
            setup_src = req.read()

    except HTTPError as exc:
        print_no("Cannot retrieve `%s`: %s" % (url_target, exc))
        print("Build should be done.")
        sys.exit(0)

    ok = True
    try:
        classifiers = [c.strip() for c in os.environ["COMPAT_CLASSIFIERS"].split(";")]
    except KeyError:
        print_no("Missing environ var `COMPAT_CLASSIFIERS`")
        print("Build should be done.")
        sys.exit(0)

    for classifier in classifiers:
        if not isinstance(classifier, bytes):
            raw_classifier = classifier.encode("utf8")
        else:
            raw_classifier = classifier
        if raw_classifier not in setup_src:
            print_no("Missing classifier `%s`" % classifier)
            ok = False
        else:
            print_ok("Found classifier `%s`" % classifier)

    if ok:
        print("Build should be done.")
        sys.exit(0)
    else:
        print("Build should not be done.")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Check project setup.py's classifiers against COMPAT_CLASSIFIERS env
        var to determine if a build must be done for this configuration.
        """
    )
    parser.add_argument("build_spec")
    args = parser.parse_args()
    build_spec = get_build_spec(args.build_spec)
    org, project = build_spec["repo"].split("/")
    commit = build_spec["commit"]
    main(org, project, commit)
