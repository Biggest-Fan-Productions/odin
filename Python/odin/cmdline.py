import csv

from odin.app import addappuser, assignappuserrole, createapp, createapprole
from odin.connection import execute_sql_file
from odin.display import listing
from odin.group import (addmembership, assignpermission, removemembership,
                        setgroup)
from odin.permission import setpermission
from odin.schema import enablemodules, migrate
from odin.user import (createuser, expireuser, setfullname, setpassword,
                       setsuperuser)

SHORTOPTS = '?d:h:p:U:'
PGOPTMAP = {
        '-d': 'dbname',
        '-h': 'host',
        '-p': 'port',
        '-U': 'user',
    }

HELPTEXT = """Manage an Odin database

    odin [opts] command [args]

opts are one or more of:

    -?                      Print this text
    -h hostname             Postgres host
    -d database             Database name
    -U username             Database username (role)

Command is one of:

    assign group permission1 [permission2 [permission3 ...]]
        Assign one or more permissions to a group.

    assign-app-user-role app_id identity_id role
        Assign user to app's role. Required `add` module.

    create-app app_id app_name [access_policy] [data_sharing_policy] [token] redirect_url]
        Create an app. Now support ony access_policy=INVITE_ONLY and data_sharing_policy=ALL
        Required `app` module.

    create-app-role app_id role
        Set up role in app. Required `app` module.

    create-app-user app_id identity_id [state]
        Add user to the app. Required `app` module.

    enable-modules mod1 [mod2 [mod3 ...]]
        Enable the modules in the Odin database schema.

    exclude username group1 [group2 [group3 ...]]
        Remove the user from the specified groups. Requires the `authz`
        module.

    expire username [time-date|never]
        Expire the identity for the user at this time.

    full-name username "Full Name"
        Set the full name field. Requires module `opts/full-name`

    help
        Show this text

    group name [description]
        Set up a group and its description.

    include filename
        Find commands (one per line) in the specified file and run them

    list [modules|users|user-groups|user-permissions]
        List information about the current configuration of the system.

    membership user group1 [group2 [group3 ...]]
        Add the user to one or more groups. Requires the `authz` module.

    migrate
        Run all migrations for the Odin database schema.

    password name [password]
        Set (or reset) the user's password. If the password is not provided
        as part of the command then the tool will prompt the user to
        enter one. Setting the password requires the module `authn`.

    permission name [description]
        Set up a permission and its description.

    sql filename
        Load the filename and present the SQL in it to the database for
        execution. This is useful for choosing migrations scripts to run.

    user username [password]
        Ensure the requested user is in the system. Setting the password
        requires the module `authn`.

        WARNING: Setting the password in this way is deprecated. Use the
        'password' command instead.

    superuser username [True|False]
        Sets the superuser bit (defaults to True). Requires the `authz`
        module.
"""


def makedsn(opts, args):
    dsnargs = {}
    for arg, opt in PGOPTMAP.items():
        if arg in opts:
            dsnargs[opt] = opts[arg]
    return ' '.join(["%s='%s'" % (n, v) for n, v in dsnargs.items()])


def include(cnx, filename):
    with open(filename, newline='') as f:
        lines = csv.reader(f, delimiter=' ')
        for line in lines:
            if len(line) and not line[0].startswith('#'):
                command(cnx, *[p for p in line if p])


COMMANDS = {
        'assign': assignpermission,
        'enable-modules': enablemodules,
        'exclude': removemembership,
        'expire': expireuser,
        'full-name': setfullname,
        'group': setgroup,
        'include': include,
        'list': listing,
        'membership': addmembership,
        'migrate': migrate,
        'password': setpassword,
        'permission': setpermission,
        'sql': execute_sql_file,
        'superuser': setsuperuser,
        'user': createuser,
        'create-app': createapp,
        'create-app-role': createapprole,
        'add-app-user': addappuser,
        'assign-app-user-role': assignappuserrole
    }


class UnknownCommand(Exception):
    pass


def command(cnx, cmd, *args):
    if cmd in COMMANDS:
        COMMANDS[cmd](cnx, *args)
    else:
        raise UnknownCommand(cmd)
