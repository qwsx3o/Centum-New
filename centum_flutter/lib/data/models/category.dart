class Category {
  final int id;
  final String name;
  final String type;
  final bool isSystem;
  final String? color;
  final String createdAt;

  const Category({
    required this.id,
    required this.name,
    required this.type,
    this.isSystem = false,
    this.color,
    this.createdAt = '',
  });

  factory Category.fromMap(Map<String, dynamic> map) {
    return Category(
      id: map['id'] as int,
      name: map['name'] as String,
      type: map['type'] as String,
      isSystem: (map['is_system'] as int) == 1,
      color: map['color'] as String?,
      createdAt: map['created_at'] as String? ?? '',
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'name': name,
      'type': type,
      'is_system': isSystem ? 1 : 0,
      'color': color,
    };
  }

  Category copyWith({
    int? id,
    String? name,
    String? type,
    bool? isSystem,
    String? color,
    String? createdAt,
  }) {
    return Category(
      id: id ?? this.id,
      name: name ?? this.name,
      type: type ?? this.type,
      isSystem: isSystem ?? this.isSystem,
      color: color ?? this.color,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}