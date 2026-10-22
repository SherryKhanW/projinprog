-- Relational form of class_dataset.schema.json
-- PostgreSQL. One student_responses row per CSV record.
-- tools and availability are unique arrays in the schema, stored here as
-- child rows so each value is one enum and cannot repeat.

CREATE TYPE school_year AS ENUM (
    'First-year',
    'Sophomore',
    'Junior',
    'Senior'
);

CREATE TYPE intro_programming AS ENUM (
    'took_it',
    'equivalent',
    'neither'
);

CREATE TYPE tool_name AS ENUM (
    'Python',
    'SQL',
    'Excel',
    'JavaScript',
    'R'
);

CREATE TYPE availability_slot AS ENUM (
    'Weekday mornings',
    'Weekday afternoons',
    'Weekday evenings',
    'Weekend mornings',
    'Weekend afternoons',
    'Weekend evenings'
);

CREATE TABLE student_responses (
    netid TEXT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    school_year school_year NOT NULL,
    intro_programming intro_programming NOT NULL,
    skill_programming SMALLINT NOT NULL,
    skill_data_stats SMALLINT NOT NULL,
    skill_frontend_design SMALLINT NOT NULL,
    skill_business_pitch SMALLINT NOT NULL,
    working_style VARCHAR(2000) NOT NULL,
    interests VARCHAR(2000) NOT NULL,
    semester_goal VARCHAR(2000) NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL,

    CONSTRAINT student_responses_netid_format CHECK (
        netid ~ '^[A-Za-z]{2,3}[0-9]{3,4}$'
        OR netid ~ '^N[0-9]{8}$'
        OR netid ~ '^[A-Za-z]{2,3}[0-9]{3,4}@nyu\.edu$'
    ),
    CONSTRAINT student_responses_name_length CHECK (
        char_length(name) BETWEEN 1 AND 80
    ),
    CONSTRAINT student_responses_skill_programming_range CHECK (
        skill_programming BETWEEN 1 AND 5
    ),
    CONSTRAINT student_responses_skill_data_stats_range CHECK (
        skill_data_stats BETWEEN 1 AND 5
    ),
    CONSTRAINT student_responses_skill_frontend_design_range CHECK (
        skill_frontend_design BETWEEN 1 AND 5
    ),
    CONSTRAINT student_responses_skill_business_pitch_range CHECK (
        skill_business_pitch BETWEEN 1 AND 5
    ),
    CONSTRAINT student_responses_working_style_text CHECK (
        char_length(working_style) BETWEEN 1 AND 2000
        AND working_style <> '#NAME?'
    ),
    CONSTRAINT student_responses_interests_length CHECK (
        char_length(interests) BETWEEN 1 AND 2000
    ),
    CONSTRAINT student_responses_semester_goal_length CHECK (
        char_length(semester_goal) BETWEEN 1 AND 2000
    )
);

CREATE TABLE student_tools (
    netid TEXT NOT NULL REFERENCES student_responses (netid) ON DELETE CASCADE,
    tool tool_name NOT NULL,
    PRIMARY KEY (netid, tool)
);

CREATE TABLE student_availability (
    netid TEXT NOT NULL REFERENCES student_responses (netid) ON DELETE CASCADE,
    slot availability_slot NOT NULL,
    PRIMARY KEY (netid, slot)
);

COMMENT ON TABLE student_responses IS
    'One onboarding response. netid is unique but may be a NetID, an N-number, or an @nyu.edu address.';
COMMENT ON COLUMN student_responses.intro_programming IS
    'took_it = completed the course; equivalent = placed out or covered elsewhere; neither = no prior course.';
COMMENT ON COLUMN student_responses.skill_programming IS
    'Self-rating from 1 (low) to 5 (high).';
COMMENT ON COLUMN student_responses.skill_data_stats IS
    'Self-rating from 1 (low) to 5 (high).';
COMMENT ON COLUMN student_responses.skill_frontend_design IS
    'Self-rating from 1 (low) to 5 (high).';
COMMENT ON COLUMN student_responses.skill_business_pitch IS
    'Self-rating from 1 (low) to 5 (high).';
COMMENT ON COLUMN student_responses.working_style IS
    'Free-text collaboration preference. The Excel sentinel #NAME? is rejected.';
COMMENT ON COLUMN student_responses.interests IS
    'Free text. May be a comma list, prose, or a newline-separated list.';
COMMENT ON COLUMN student_responses.submitted_at IS
    'Form submission time, stored with time zone.';
COMMENT ON TABLE student_tools IS
    'Tools a student listed. At least one row per student; the primary key blocks duplicates.';
COMMENT ON TABLE student_availability IS
    'Meeting slots a student marked. At least one row per student; the primary key blocks duplicates.';
