class Transaction {
  final int id;
  final String type;
  final double amount;
  final int categoryId;
  final String categoryName;
  final String note;
  final String createdAt;

  const Transaction({
    required this.id,
    required this.type,
    required this.amount,
    required this.categoryId,
    this.categoryName = '',
    this.note = '',
    this.createdAt = '',
  });

  factory Transaction.fromMap(Map<String, dynamic> map) {
    return Transaction(
      id: map['id'] as int,
      type: map['type'] as String,
      amount: (map['amount'] as num).toDouble(),
      categoryId: map['category_id'] as int,
      categoryName: map['category_name'] as String? ?? '',
      note: map['note'] as String? ?? '',
      createdAt: map['created_at'] as String? ?? '',
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'type': type,
      'amount': amount,
      'category_id': categoryId,
      'note': note,
    };
  }
}

class FinanceSummary {
  final double totalIncome;
  final double totalCapital;
  final double totalExpenses;
  final double spendable;
  final double available;

  const FinanceSummary({
    this.totalIncome = 0,
    this.totalCapital = 0,
    this.totalExpenses = 0,
    this.spendable = 0,
    this.available = 0,
  });
}

class PieSegment {
  final String label;
  final double value;
  final String color;
  final bool isCapital;

  const PieSegment({
    required this.label,
    required this.value,
    required this.color,
    this.isCapital = false,
  });
}

class MonthlySummary {
  final double income;
  final double capital;
  final double expenses;
  final int year;
  final int month;

  const MonthlySummary({
    this.income = 0,
    this.capital = 0,
    this.expenses = 0,
    required this.year,
    required this.month,
  });
}

class DayGroup {
  final String date;
  final List<Transaction> transactions;
  final double income;
  final double capital;
  final double expenses;

  const DayGroup({
    required this.date,
    required this.transactions,
    this.income = 0,
    this.capital = 0,
    this.expenses = 0,
  });
}

class BackupInfo {
  final String name;
  final int sizeKb;
  final String created;

  const BackupInfo({
    required this.name,
    required this.sizeKb,
    required this.created,
  });
}