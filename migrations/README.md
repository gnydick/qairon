# Migration Instructions for Special Cases
Any scripts or utilities will be found in `<src>/migrations/scripts/upgrade_from_add_indexes`

## upgrade from add_indexes
1. run an upgrade just to *add_bin_map*
```
flask db upgrade add_bin_map
```
2. drop the constraints by opening the **drop_constraints.sql** file in a query console and run all.

3. add the constraints back with additional option of `on update cascade` by opening the file **add_updated_constraints.sql** 



4. then we have to read and save all of the objects to update their IDs since they're the result of concatenating their parents' IDs. we'll run the **cascade_new_ids.py** script
```
export SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://<user>:<pass>@<host>:<port>/<db>
export PYTHONPATH=$PYTHONPATH:/home/gnydick/IdeaProjects/qairon/migrations/scripts
./migrations/scripts/cascade_new_ids.py
```

5. if there are no more instructions in this file, then you can resume upgrading the database, otherwise, follow the next section
```
flask db upgrade
```