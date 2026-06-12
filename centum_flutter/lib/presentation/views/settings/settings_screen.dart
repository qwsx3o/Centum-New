import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:centum/presentation/bloc/settings/settings_cubit.dart';
import 'package:centum/presentation/bloc/settings/settings_state.dart';
import 'package:centum/core/theme/app_theme.dart';
import 'package:centum/core/constants/dimensions.dart';
import 'package:centum/presentation/views/settings/widgets/profile_section.dart';
import 'package:centum/presentation/views/settings/widgets/categories_section.dart';
import 'package:centum/presentation/views/settings/widgets/backup_section.dart';
import 'package:centum/presentation/views/settings/widgets/danger_zone_section.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: BlocBuilder<SettingsCubit, SettingsState>(
        builder: (context, state) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(Dimensions.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Настройки',
                  style: TextStyle(
                    fontSize: Dimensions.textXxl,
                    fontWeight: FontWeight.bold,
                    color: AppColors.text,
                  ),
                ),
                const SizedBox(height: Dimensions.md),
                ProfileSection(
                  familyMembers: state.familyMembers,
                  onChanged: (v) {
                    context
                        .read<SettingsCubit>()
                        .updateSettings('profile', 'family_members', v);
                  },
                ),
                const SizedBox(height: Dimensions.md),
                const CategoriesSection(),
                const SizedBox(height: Dimensions.md),
                const BackupSection(),
                const SizedBox(height: Dimensions.md),
                const DangerZoneSection(),
                const SizedBox(height: Dimensions.xl),
              ],
            ),
          );
        },
      ),
    );
  }
}