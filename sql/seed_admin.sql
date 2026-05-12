CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(160) NOT NULL,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(180) NOT NULL UNIQUE,
    password_hash VARCHAR(260) NOT NULL,
    role VARCHAR(40) NOT NULL,
    branch VARCHAR(160) NOT NULL DEFAULT 'Төв салбар',
    status VARCHAR(24) NOT NULL DEFAULT 'Active',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_admin_users_id ON admin_users (id);
CREATE INDEX IF NOT EXISTS ix_admin_users_username ON admin_users (username);
CREATE INDEX IF NOT EXISTS ix_admin_users_email ON admin_users (email);
CREATE INDEX IF NOT EXISTS ix_admin_users_role ON admin_users (role);
CREATE INDEX IF NOT EXISTS ix_admin_users_status ON admin_users (status);

INSERT INTO admin_users (
    name,
    username,
    email,
    password_hash,
    role,
    branch,
    status,
    is_deleted,
    updated_at
)
VALUES (
    'Төв Админ',
    'admin',
    'admin@bichil.mn',
    'pbkdf2_sha256$210000$feedback-admin-seed$hzRa5xJqfBfmTGUlJZRukp1lL4vG2bTqbfAPC4tPGmg=',
    'super_admin',
    'Төв салбар',
    'Active',
    FALSE,
    now()
)
ON CONFLICT (username) DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    branch = EXCLUDED.branch,
    status = EXCLUDED.status,
    is_deleted = FALSE,
    updated_at = now();
