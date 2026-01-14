# When it is necessary to change relationships and re-key objects
Any scripts or utilities will be found in `<src>/migrations/scripts

1. drop the constraints by opening the **drop_constraints.sql** file in a query console and run all.

2. run migrations or other changes needed that require the dropping of constraints

1. add the constraints back with additional option of `on update cascade` by opening the file **add_updated_constraints.sql** 

1. then we have to read and save all of the objects to update their IDs since they're the result of concatenating their parents' IDs. we'll run the **cascade_new_ids.py** script
    ```
    export SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://<user>:<pass>@<host>:<port>/<db>
    export PYTHONPATH=$PYTHONPATH:/home/gnydick/IdeaProjects/qairon/migrations/scripts
    ./migrations/scripts/cascade_new_ids.py
    ```