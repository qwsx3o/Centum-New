import 'package:centum/core/constants/app_constants.dart';
import 'package:centum/data/models/transaction.dart';
import 'package:centum/data/repositories/category_repository.dart';
import 'package:centum/data/repositories/transaction_repository.dart';

class FinanceService {
  Future<Map<String, dynamic>> addIncome(
    double amount,
    int categoryId, {
    String note = '',
  }) async {
    if (amount <= 0) {
      throw ArgumentError('Сумма должна быть больше 0');
    }

    final capitalAmount = amount * AppConstants.capitalRate;
    final availableAmount = amount * (1 - AppConstants.capitalRate);

    final capitalCategory = await CategoryRepository.getCategoryByName(
      AppConstants.capitalCategoryName,
    );

    final incomeTx = await TransactionRepository.createTransaction(
      'income',
      amount,
      categoryId,
      note: note,
    );

    final capitalTx = await TransactionRepository.createTransaction(
      'capital',
      capitalAmount,
      capitalCategory!.id,
      note: 'Авто: 10% от дохода #${incomeTx.id}',
    );

    return {
      'income_tx': incomeTx,
      'capital_tx': capitalTx,
      'capital_amount': capitalAmount,
      'available_amount': availableAmount,
    };
  }

  Future<Transaction> addExpense(
    double amount,
    int categoryId, {
    String note = '',
  }) async {
    if (amount <= 0) {
      throw ArgumentError('Сумма должна быть больше 0');
    }

    final summary = await TransactionRepository.getSummary();
    if (amount > summary.available) {
      throw ArgumentError('Недостаточно средств');
    }

    return TransactionRepository.createTransaction(
      'expense',
      amount,
      categoryId,
      note: note,
    );
  }

  Future<FinanceSummary> getSummary() {
    return TransactionRepository.getSummary();
  }

  Future<List<PieSegment>> getPieChartData() async {
    final summary = await TransactionRepository.getSummary();
    final expensesByCategory = await TransactionRepository
        .getExpensesByCategory();

    final segments = <PieSegment>[];

    for (final segment in expensesByCategory) {
      if (segment.isCapital) {
        segments.add(PieSegment(
          label: segment.label,
          value: segment.value,
          color: '#C9A84C',
          isCapital: true,
        ));
      }
    }

    for (final segment in expensesByCategory) {
      if (!segment.isCapital && segment.value > 0) {
        segments.add(segment);
      }
    }

    if (summary.available > 0) {
      segments.add(PieSegment(
        label: 'Доступно',
        value: summary.available,
        color: '#42A5F5',
        isCapital: false,
      ));
    }

    return segments;
  }

  Future<List<Transaction>> getHistory({int limit = 100}) {
    return TransactionRepository.getAllTransactions(limit: limit);
  }

  Future<void> deleteTransaction(int id) {
    return TransactionRepository.deleteTransaction(id);
  }
}