import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart' as p;
import '../constants/app_constants.dart';

class DatabaseHelper {
  static Database? _db;

  static Future<Database> get instance async {
    if (_db != null) return _db!;
    _db = await _init();
    return _db!;
  }

  static Future<Database> _init() async {
    final dbPath = await getDatabasesPath();
    final path = p.join(dbPath, AppConstants.dbName);
    return openDatabase(
      path,
      version: AppConstants.dbVersion,
      onCreate: _onCreate,
    );
  }

  static Future<void> _onCreate(Database db, int version) async {
    await db.execute('''
      CREATE TABLE categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        type TEXT NOT NULL CHECK(type IN ('income','expense','system')),
        is_system INTEGER NOT NULL DEFAULT 0,
        color TEXT DEFAULT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
      )
    ''');

    await db.execute('''
      CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL CHECK(type IN ('income','expense','capital')),
        amount REAL NOT NULL CHECK(amount > 0),
        category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
        note TEXT DEFAULT '',
        created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
      )
    ''');

    await db.execute(
      'CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at DESC)',
    );
    await db.execute(
      'CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type)',
    );

    await db.execute('PRAGMA journal_mode=WAL');
    await db.execute('PRAGMA foreign_keys=ON');

    await db.insert('categories', {
      'name': AppConstants.capitalCategoryName,
      'type': 'system',
      'is_system': 1,
      'color': '#C9A84C',
    });

    await db.insert('categories', {
      'name': AppConstants.defaultIncomeCategory,
      'type': 'income',
      'is_system': 1,
      'color': '#4CAF50',
    });
  }

  static Future<void> close() async {
    await _db?.close();
    _db = null;
  }
}