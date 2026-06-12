import '../../core/database/database_helper.dart';
import '../models/transaction.dart';

class TransactionRepository {
  static Future<List<Transaction>> getAllTransactions({
    int limit = 100,
    int offset = 0,
  }) async {
    final db = await DatabaseHelper.instance;
    final maps = await db.rawQuery('''
      SELECT t.*, c.name as category_name
      FROM transactions t
      JOIN categories c ON t.category_id = c.id
      ORDER BY t.created_at DESC
      LIMIT ? OFFSET ?
    ''', [limit, offset]);
    return maps.map((map) => Transaction.fromMap(map)).toList();
  }

  static Future<List<Transaction>> getTransactionsByType(String type) async {
    final db = await DatabaseHelper.instance;
    final maps = await db.rawQuery('''
      SELECT t.*, c.name as category_name
      FROM transactions t
      JOIN categories c ON t.category_id = c.id
      WHERE t.type = ?
      ORDER BY t.created_at DESC
    ''', [type]);
    return maps.map((map) => Transaction.fromMap(map)).toList();
  }

  static Future<FinanceSummary> getSummary() async {
    final db = await DatabaseHelper.instance;
    final result = await db.rawQuery('''
      SELECT
        COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
        COALESCE(SUM(CASE WHEN type = 'capital' THEN amount ELSE 0 END), 0) as total_capital,
        COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expenses
      FROM transactions
    ''');
    final row = result.first;
    final totalIncome = (row['total_income'] as num).toDouble();
    final totalCapital = (row['total_capital'] as num).toDouble();
    final totalExpenses = (row['total_expenses'] as num).toDouble();
    return FinanceSummary(
      totalIncome: totalIncome,
      totalCapital: totalCapital,
      totalExpenses: totalExpenses,
      spendable: totalIncome - totalExpenses,
      available: totalIncome + totalCapital - totalExpenses,
    );
  }

  static Future<List<PieSegment>> getExpensesByCategory() async {
    final db = await DatabaseHelper.instance;
    final maps = await db.rawQuery('''
      SELECT
        c.name as label,
        SUM(t.amount) as value,
        COALESCE(c.color, '#999999') as color,
        CASE WHEN c.type = 'capital' THEN 1 ELSE 0 END as is_capital
      FROM transactions t
      JOIN categories c ON t.category_id = c.id
      GROUP BY t.category_id
      ORDER BY value DESC
    ''');
    return maps.map((map) => PieSegment(
      label: map['label'] as String,
      value: (map['value'] as num).toDouble(),
      color: map['color'] as String,
      isCapital: (map['is_capital'] as int) == 1,
    )).toList();
  }

  static Future<MonthlySummary> getMonthlySummary(
    int year,
    int month,
  ) async {
    final db = await DatabaseHelper.instance;
    final monthStr = '$year-${month.toString().padLeft(2, '0')}';
    final result = await db.rawQuery('''
      SELECT
        COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as income,
        COALESCE(SUM(CASE WHEN type = 'capital' THEN amount ELSE 0 END), 0) as capital,
        COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as expenses
      FROM transactions
      WHERE strftime('%Y-%m', created_at) = ?
    ''', [monthStr]);
    final row = result.first;
    return MonthlySummary(
      income: (row['income'] as num).toDouble(),
      capital: (row['capital'] as num).toDouble(),
      expenses: (row['expenses'] as num).toDouble(),
      year: year,
      month: month,
    );
  }

  static Future<List<Transaction>> getTransactionsForMonth(
    int year,
    int month,
  ) async {
    final db = await DatabaseHelper.instance;
    final monthStr = '$year-${month.toString().padLeft(2, '0')}';
    final maps = await db.rawQuery('''
      SELECT t.*, c.name as category_name
      FROM transactions t
      JOIN categories c ON t.category_id = c.id
      WHERE strftime('%Y-%m', t.created_at) = ?
      ORDER BY t.created_at DESC
    ''', [monthStr]);
    return maps.map((map) => Transaction.fromMap(map)).toList();
  }

  static Future<List<DayGroup>> getDaysWithTransactions(
    int year,
    int month,
  ) async {
    final transactions = await getTransactionsForMonth(year, month);
    final Map<String, List<Transaction>> grouped = {};
    for (final t in transactions) {
      final date = t.createdAt.length >= 10
          ? t.createdAt.substring(0, 10)
          : t.createdAt;
      grouped.putIfAbsent(date, () => []).add(t);
    }
    final sortedDates = grouped.keys.toList()..sort((a, b) => b.compareTo(a));
    return sortedDates.map((date) {
      final dayTxns = grouped[date]!;
      double income = 0, capital = 0, expenses = 0;
      for (final t in dayTxns) {
        switch (t.type) {
          case 'income':
            income += t.amount;
          case 'capital':
            capital += t.amount;
          case 'expense':
            expenses += t.amount;
        }
      }
      return DayGroup(
        date: date,
        transactions: dayTxns,
        income: income,
        capital: capital,
        expenses: expenses,
      );
    }).toList();
  }

  static Future<Transaction> createTransaction(
    String type,
    double amount,
    int categoryId, {
    String note = '',
  }) async {
    final db = await DatabaseHelper.instance;
    final id = await db.insert('transactions', {
      'type': type,
      'amount': amount,
      'category_id': categoryId,
      'note': note,
    });
    final maps = await db.rawQuery('''
      SELECT t.*, c.name as category_name
      FROM transactions t
      JOIN categories c ON t.category_id = c.id
      WHERE t.id = ?
    ''', [id]);
    return Transaction.fromMap(maps.first);
  }

  static Future<void> deleteTransaction(int id) async {
    final db = await DatabaseHelper.instance;
    await db.delete('transactions', where: 'id = ?', whereArgs: [id]);
  }
}