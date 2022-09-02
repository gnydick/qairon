SELECT CONCAT('alter table ',conrelid::regclass, chr(13), '    ',
              ' add constraint ', conname,' ', chr(13), '        ',
              pg_get_constraintdef(oid), chr(13), '            '
              'on update cascade;')
FROM   pg_constraint
WHERE  contype = 'f'
  AND    connamespace = 'public'::regnamespace
ORDER  BY conrelid::regclass::text, contype DESC;


