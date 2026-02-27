-- Drop existing table
DROP TABLE IF EXISTS opportunities CASCADE;
DROP TABLE IF EXISTS opportunity_skills CASCADE;
DROP TABLE IF EXISTS skills CASCADE;
DROP TABLE IF EXISTS providers CASCADE;

-- 1. Create providers table
CREATE TABLE providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL
);

-- 2. Create skills table
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL
);

-- 3. Create opportunities table (Main table)
CREATE TABLE opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type TEXT NOT NULL, -- 'internship', 'course', 'event', 'certification', 'job'
    title TEXT NOT NULL,
    provider_id UUID REFERENCES providers(id) ON DELETE SET NULL,
    url TEXT UNIQUE NOT NULL, -- Used to avoid duplicates during upsert
    description TEXT,
    location TEXT,
    posted_date TEXT,
    source TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create opportunity_skills junction table (N:M relationship)
CREATE TABLE opportunity_skills (
    opportunity_id UUID REFERENCES opportunities(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (opportunity_id, skill_id)
);

-- Allow anonymous access (if your frontend/backend needs it or if you use RLS)
-- Depending on your setup, you might want these:
-- ALTER TABLE providers ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE opportunities ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE opportunity_skills ENABLE ROW LEVEL SECURITY;

-- Basic policies to allow reading without authentication for development
-- CREATE POLICY "Allow public read-only access" ON providers FOR SELECT USING (true);
-- CREATE POLICY "Allow public read-only access" ON skills FOR SELECT USING (true);
-- CREATE POLICY "Allow public read-only access" ON opportunities FOR SELECT USING (true);
-- CREATE POLICY "Allow public read-only access" ON opportunity_skills FOR SELECT USING (true);

-- The old setup didn't seem to enforce strict RLS based on the python code using service keys, 
-- but if using a publishable key (anon key), you need to allow access. 
-- For now, if your DB allows all, we just create the tables.
