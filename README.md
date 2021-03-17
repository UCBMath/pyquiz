# pyquiz

This is a domain-specific language for authoring Canvas quizzes.  It
is designed for with an eye toward
1. making it easy to have a ready library of questions to create new quizzes and
2. making it easy to generate variants of questions (making use of question groups).

The way in which quiz questions are authored is somewhat inspired by
WeBWorK.

## Setting up

- Clone this repository.  If you are using the command line, use `git clone https://github.com/UCBMath/pyquiz.git` to create a folder called `pyquiz`.
- Make sure you have Python 3 installed.
- [https://github.com/ucfopen/canvasapi](canvasapi).  Install with `pip3 install --user canvasapi`
