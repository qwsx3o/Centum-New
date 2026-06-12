import 'package:flutter_test/flutter_test.dart';
import 'package:centum/main.dart';

void main() {
  testWidgets('App renders without error', (WidgetTester tester) async {
    await tester.pumpWidget(const CentumApp());
    expect(find.text('CENTUM'), findsWidgets);
  });
}