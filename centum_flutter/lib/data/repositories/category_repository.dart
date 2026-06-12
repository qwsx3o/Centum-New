import 'package:sqflite/sqflite.dart';
import '../../core/database/database_helper.dart';
import '../models/category.dart';

class CategoryRepository {
  static Future<List<Category>> getAllCategories() async {
    final db = await DatabaseHelper.instance;
    final maps = await db.query(
      'categories',
      orderBy: 'is_system DESC, name ASC',
    );
    return maps.map((map) => Category.fromMap(map)).toList();
  }

  static Future<List<Category>> getCategoriesByType(String type) async {
    final db = await DatabaseHelper.instance;
    final maps = await db.query(
      'categories',
      where: 'type = ?',
      whereArgs: [type],
      orderBy: 'name ASC',
    );
    return maps.map((map) => Category.fromMap(map)).toList();
  }

  static Future<Category?> getCategoryById(int id) async {
    final db = await DatabaseHelper.instance;
    final maps = await db.query(
      'categories',
      where: 'id = ?',
      whereArgs: [id],
    );
    if (maps.isEmpty) return null;
    return Category.fromMap(maps.first);
  }

  static Future<Category?> getCategoryByName(String name) async {
    final db = await DatabaseHelper.instance;
    final maps = await db.query(
      'categories',
      where: 'name = ?',
      whereArgs: [name],
    );
    if (maps.isEmpty) return null;
    return Category.fromMap(maps.first);
  }

  static Future<Category> createCategory(
    String name,
    String type,
    String? color,
  ) async {
    final db = await DatabaseHelper.instance;
    final id = await db.insert('categories', {
      'name': name,
      'type': type,
      'is_system': 0,
      'color': color,
    });
    final maps = await db.query(
      'categories',
      where: 'id = ?',
      whereArgs: [id],
    );
    return Category.fromMap(maps.first);
  }

  static Future<bool> deleteCategory(int id) async {
    final db = await DatabaseHelper.instance;
    final category = await getCategoryById(id);
    if (category == null) return false;
    if (category.isSystem) return false;
    final count = Sqflite.firstIntValue(
      await db.rawQuery(
        'SELECT COUNT(*) FROM transactions WHERE category_id = ?',
        [id],
      ),
    );
    if (count != null && count > 0) return false;
    await db.delete('categories', where: 'id = ?', whereArgs: [id]);
    return true;
  }
}