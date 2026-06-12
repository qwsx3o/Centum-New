import 'package:flutter/material.dart';
import 'package:centum/core/theme/app_theme.dart';
import 'package:centum/core/constants/dimensions.dart';

class ProfileSection extends StatelessWidget {
  final int familyMembers;
  final ValueChanged<int> onChanged;

  const ProfileSection({
    super.key,
    required this.familyMembers,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.card,
      child: Padding(
        padding: const EdgeInsets.all(Dimensions.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Профиль',
                style: TextStyle(
                  fontSize: Dimensions.textLg,
                  fontWeight: FontWeight.bold,
                  color: AppColors.text,
                )),
            const SizedBox(height: Dimensions.md),
            Row(
              children: [
                const Text('Членов семьи:',
                    style: TextStyle(color: AppColors.subtext)),
                const Spacer(),
                IconButton(
                  onPressed: familyMembers > 1
                      ? () => onChanged(familyMembers - 1)
                      : null,
                  icon: const Icon(Icons.remove),
                  color: familyMembers > 1
                      ? AppColors.text
                      : AppColors.muted,
                ),
                Text('$familyMembers',
                    style: const TextStyle(
                      fontSize: Dimensions.textXl,
                      fontWeight: FontWeight.bold,
                      color: AppColors.text,
                    )),
                IconButton(
                  onPressed: () => onChanged(familyMembers + 1),
                  icon: const Icon(Icons.add),
                  color: AppColors.text,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}