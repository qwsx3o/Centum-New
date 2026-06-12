import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:centum/core/theme/app_theme.dart';
import 'package:centum/core/constants/dimensions.dart';
import 'package:centum/data/models/transaction.dart';

class DonutChart extends StatelessWidget {
  final List<PieSegment> segments;
  final String centerLabel;
  final String centerSubLabel;

  const DonutChart({
    super.key,
    required this.segments,
    required this.centerLabel,
    required this.centerSubLabel,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: Dimensions.donutSize,
      height: Dimensions.donutSize,
      child: Stack(
        alignment: Alignment.center,
        children: [
          CustomPaint(
            size: const Size(Dimensions.donutSize, Dimensions.donutSize),
            painter: _DonutPainter(segments: segments),
          ),
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                centerLabel,
                style: const TextStyle(
                  fontSize: Dimensions.textXl,
                  fontWeight: FontWeight.bold,
                  color: AppColors.text,
                ),
              ),
              Text(
                centerSubLabel,
                style: const TextStyle(
                  fontSize: Dimensions.textSm,
                  color: AppColors.subtext,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _DonutPainter extends CustomPainter {
  final List<PieSegment> segments;

  _DonutPainter({required this.segments});

  @override
  void paint(Canvas canvas, Size size) {
    if (segments.isEmpty) return;

    final total = segments.fold<double>(0, (sum, s) => sum + s.value);
    if (total <= 0) return;

    final center = Offset(size.width / 2, size.height / 2);
    const outerRadius = Dimensions.donutOuterRadius;
    const innerRadius = Dimensions.donutInnerRadius;
    final paint = Paint()
      ..style = PaintingStyle.fill
      ..strokeWidth = 0;

    double startAngle = -math.pi / 2;

    for (final seg in segments) {
      final sweepAngle = (seg.value / total) * 2 * math.pi;
      final color = Color(int.parse(seg.color.replaceFirst('#', '0xFF')));

      paint.color = color;

      final path = _createArcPath(center, outerRadius, innerRadius, startAngle, sweepAngle);
      canvas.drawPath(path, paint);

      startAngle += sweepAngle;
    }
  }

  Path _createArcPath(
    Offset center,
    double outerRadius,
    double innerRadius,
    double startAngle,
    double sweepAngle,
  ) {
    final path = Path();

    path.arcTo(
      Rect.fromCircle(center: center, radius: outerRadius),
      startAngle,
      sweepAngle,
      false,
    );

    final innerStartAngle = startAngle + sweepAngle;
    path.arcTo(
      Rect.fromCircle(center: center, radius: innerRadius),
      innerStartAngle,
      -sweepAngle,
      false,
    );

    path.close();
    return path;
  }

  @override
  bool shouldRepaint(covariant _DonutPainter old) {
    return old.segments != segments;
  }
}