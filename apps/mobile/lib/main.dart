import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  runApp(const ProviderScope(child: ParkcapApp()));
}

class ParkcapApp extends StatelessWidget {
  const ParkcapApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ParkCAP',
      theme: ThemeData.dark(),
      home: const Scaffold(
        body: Center(child: Text('ParkCAP Mobile')),
      ),
    );
  }
}
