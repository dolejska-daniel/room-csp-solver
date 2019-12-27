# Room CSP solver
> v1.0

Room constraint satisfaction problem solver application.
This application provides simple, yet powerful, interface for room assignment management.

## Features
- Participant requirements (someone requires to be accomodated with someone else)
- Room type policy (participants with specific type can only be accomodated in rooms with the same type)
- Same gender room policy 

## Installation
Application excecutables can be downloaded on [releases page](https://github.com/dolejska-daniel/room-csp-solver/releases).

Sources for development can be downloaded via `git`.
Required Python packages can then be installed via `pipenv`.
Executables can be built via `pyinstaller`.
```shell script
git clone git@github.com:dolejska-daniel/room-csp-solver.git
cd room-csp-solver
pipenv install
```

## Controls
Application can be controlled via window menu or corresponding keyboard shortcuts.

Double click allows records to be edited/toggled.

Pressing delete button removes selected records permanently.
