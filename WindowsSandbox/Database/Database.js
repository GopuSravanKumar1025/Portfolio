const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');

const dbPath = 'C:/Users/WDAGUtilityAccount/Desktop/SandBoxDb.db';
console.log('Database path:', dbPath);

// Check if the database file exists
fs.access(dbPath, fs.constants.F_OK, (err) => {
    if (err) {
      console.log('Database file does not exist. Creating a new one...');
    } else {
      console.log('Database file exists. Connecting to the database...');
    }
  
    // Create or connect to the database
    const db = new sqlite3.Database(dbPath, (err) => {
      if (err) {
        console.error('Error connecting to the database:', err.message);
      } else {
        console.log('Connected to SQLite database.');
        initializeDatabase(db);
      }
    });
  });

function initializeDatabase(db) {
  db.run(`PRAGMA foreign_keys = ON;`, (err) => {
    if (err) {
      console.error('Error enabling foreign keys:', err.message);
    } else {
      console.log('Foreign keys enabled.');
    }
  });

  db.run(`PRAGMA user_version = 2;`, (err) => {
    if (err) {
      console.error('Error setting user version:', err.message);
    } else {
      console.log('User version set to 2.');
    }
  });

  db.run('BEGIN TRANSACTION;', (err) => {
    if (err) {
      console.error('Error starting transaction:', err.message);
    } else {
      console.log('Transaction started.');
    }
  });

  const sqlCommands = [
    `CREATE TABLE import_operations (
        iid INTEGER PRIMARY KEY,
        created_on DATETIME NOT NULL,
        last_update DATETIME,
        import_status INTEGER NOT NULL,
        uuid VARCHAR(36) UNIQUE NOT NULL
      );`,
      `CREATE TABLE studies (
        iid INTEGER PRIMARY KEY,
        created_on DATETIME NOT NULL,
        removed_on DATETIME,
        last_update DATETIME NOT NULL,
        import_operation_iid INTEGER,
        study_instance_uid VARCHAR(64) NOT NULL,
        metadata_jsonb BLOB NOT NULL,
        metadata_version INTEGER NOT NULL,
        FOREIGN KEY(import_operation_iid) REFERENCES import_operations(iid)
      );`,
      `CREATE TABLE instances (
        iid INTEGER PRIMARY KEY,
        created_on DATETIME NOT NULL,
        removed_on DATETIME,
        deletion_status INTEGER,
        sop_instance_uid VARCHAR(64) NOT NULL,
        series_instance_uid VARCHAR(64) NOT NULL,
        study_iid INTEGER NOT NULL,
        relative_file_path TEXT UNIQUE NOT NULL,
        offset_in_file INTEGER,
        instance_size INTEGER NOT NULL,
        file_status INTEGER NOT NULL,
        checksum CHAR(64) NOT NULL,
        FOREIGN KEY(study_iid) REFERENCES studies(iid)
      );`,
      
      `CREATE TABLE incompete_file_chunks (
        import_operation_iid INTEGER NOT NULL,
        instance_iid INTEGER NOT NULL,
        FOREIGN KEY(import_operation_iid) REFERENCES import_operations(iid),
        FOREIGN KEY(instance_iid) REFERENCES instances(iid),
        PRIMARY KEY(import_operation_iid, instance_iid)
      );`,
      `CREATE TABLE config (
        name TEXT PRIMARY KEY,
        value TEXT
      );`
    // Other table creation commands...
  ];

  let remaining = sqlCommands.length;

  sqlCommands.forEach((sql) => {
    // Improved regular expression to handle extra spaces and new lines
    const tableNameMatch = sql.match(/CREATE TABLE\s+([^\s(]+)/i);
    
    if (tableNameMatch) {
      const tableName = tableNameMatch[1];

      // Check if the table already exists
      db.get(`SELECT name FROM sqlite_master WHERE type='table' AND name='${tableName}';`, (err, row) => {
        if (err) {
          console.error('Error checking table existence:', err.message);
        } else if (!row) {
          // Table doesn't exist, run the query
          db.run(sql, (err) => {
            if (err) {
              console.error('Error executing SQL:', err.message);
            } else {
              console.log(`Table ${tableName} created successfully.`);
            }
          });
        } else {
          console.log(`Table ${tableName} already exists. Skipping creation.`);
        }

        remaining -= 1;
        if (remaining === 0) {
          db.run('COMMIT;', (err) => {
            if (err) {
              console.error('Error committing transaction:', err.message);
            } else {
              console.log('Transaction committed.');
            }

            fetchTables(db);
          });
        }
      });
    } else {
      console.error('Failed to match table name in SQL:', sql);
    }
  });
}

function fetchTables(db) {
  db.all("SELECT name FROM sqlite_master WHERE type='table';", (err, tables) => {
    if (err) {
      console.error('Error fetching tables:', err.message);
    } else {
      console.log('Existing tables:', tables);
    }

    db.close((err) => {
      if (err) {
        console.error('Error closing the database:', err.message);
      } else {
        console.log('Database connection closed.');
      }
    });
  });
}


























































//`CREATE UNIQUE INDEX idx_studies_studyinstanceuid_importoperationiid ON studies (
    //     import_operation_iid,
    //     study_instance_uid
    //   ) WHERE removed_on ISNULL;`,
    //   `CREATE UNIQUE INDEX idx_instances_sopinstanceuid_studyiid ON instances (
    //     study_iid,
    //     sop_instance_uid
    //   ) WHERE removed_on ISNULL;`,