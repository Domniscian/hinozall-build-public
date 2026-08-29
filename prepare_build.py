from pathlib import Path

root = Path("work")
home = root / "app/src/main/java/com/domniscian/app/ui/screens/HomeScreen.kt"
build = root / "app/build.gradle.kts"
text = home.read_text(encoding="utf-8")

if "private fun ActivityDayClock(" not in text:
    text = text.replace(
        "import androidx.compose.foundation.BorderStroke\n",
        "import androidx.compose.foundation.BorderStroke\nimport androidx.compose.foundation.Canvas\n",
        1,
    )
    text = text.replace(
        "import androidx.compose.ui.graphics.Color\n",
        "import androidx.compose.ui.graphics.Color\nimport androidx.compose.ui.graphics.StrokeCap\nimport androidx.compose.ui.graphics.drawscope.Stroke\nimport androidx.compose.ui.graphics.nativeCanvas\nimport androidx.compose.ui.graphics.toArgb\n",
        1,
    )
    text = text.replace(
        "import androidx.compose.ui.unit.dp\n",
        "import androidx.compose.ui.unit.dp\nimport androidx.compose.ui.unit.sp\n",
        1,
    )
    text = text.replace(
        "import java.time.LocalDate\n",
        "import java.time.LocalDate\nimport java.time.ZoneId\nimport kotlin.math.cos\nimport kotlin.math.sin\n",
        1,
    )

    marker = '''            item {
                SectionHeader(
                    "Historique d’activité",'''
    replacement = '''            item {
                ActivityDayClock(periods = periods)
            }

            item {
                SectionHeader(
                    "Historique d’activité",'''
    if marker not in text:
        raise SystemExit("History marker not found: refusing to build the wrong UI source")
    text = text.replace(marker, replacement, 1)

    marker2 = '''@Composable
private fun SummaryStat(label: String, value: String, accent: Color, modifier: Modifier = Modifier) {'''
    clock = '''@Composable
private fun ActivityDayClock(periods: List<ActivityPeriod>) {
    val zone = remember { ZoneId.systemDefault() }
    val today = LocalDate.now(zone)
    val dayStart = remember(today, zone) { today.atStartOfDay(zone).toInstant().toEpochMilli() }
    val dayEnd = remember(today, zone) { today.plusDays(1).atStartOfDay(zone).toInstant().toEpochMilli() }
    val now = System.currentTimeMillis()
    val visiblePeriods = periods.mapNotNull { period ->
        val rawStart = period.startAt ?: return@mapNotNull null
        val rawEnd = period.endAt ?: now
        val start = rawStart.coerceAtLeast(dayStart)
        val end = rawEnd.coerceAtMost(dayEnd)
        if (end > start) start to end else null
    }
    val primary = MaterialTheme.colorScheme.primary
    val outline = MaterialTheme.colorScheme.outline
    val onSurface = MaterialTheme.colorScheme.onSurface
    val surfaceVariant = MaterialTheme.colorScheme.surfaceVariant
    val density = LocalDensity.current
    val textSizePx = with(density) { 11.sp.toPx() }
    val labelPaint = remember { android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG) }.apply {
        color = onSurface.toArgb()
        textAlign = android.graphics.Paint.Align.CENTER
        textSize = textSizePx
        typeface = android.graphics.Typeface.create(android.graphics.Typeface.DEFAULT, android.graphics.Typeface.BOLD)
    }

    Panel(Modifier.fillMaxWidth(), PaddingValues(horizontal = 16.dp, vertical = 16.dp)) {
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            Text("Aujourd’hui", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold)
            Spacer(Modifier.weight(1f))
            Text(
                if (visiblePeriods.isEmpty()) "Aucune activité" else "${visiblePeriods.size} session${if (visiblePeriods.size > 1) "s" else ""}",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Spacer(Modifier.height(12.dp))
        Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
            Canvas(Modifier.size(252.dp)) {
                val center = androidx.compose.ui.geometry.Offset(size.width / 2f, size.height / 2f)
                val radius = size.minDimension * 0.37f
                val arcRadius = radius - 3.dp.toPx()
                val arcTopLeft = androidx.compose.ui.geometry.Offset(center.x - arcRadius, center.y - arcRadius)
                val arcSize = androidx.compose.ui.geometry.Size(arcRadius * 2f, arcRadius * 2f)

                drawCircle(
                    color = surfaceVariant.copy(alpha = .55f),
                    radius = radius + 18.dp.toPx(),
                    center = center,
                )
                drawCircle(
                    color = outline.copy(alpha = .22f),
                    radius = radius,
                    center = center,
                    style = Stroke(width = 2.dp.toPx()),
                )

                for (hour in 0 until 24) {
                    val angle = Math.toRadians((hour * 15.0) - 90.0)
                    val major = hour % 3 == 0
                    val outer = radius + 10.dp.toPx()
                    val inner = radius + if (major) 1.dp.toPx() else 5.dp.toPx()
                    val start = androidx.compose.ui.geometry.Offset(
                        center.x + cos(angle).toFloat() * inner,
                        center.y + sin(angle).toFloat() * inner,
                    )
                    val end = androidx.compose.ui.geometry.Offset(
                        center.x + cos(angle).toFloat() * outer,
                        center.y + sin(angle).toFloat() * outer,
                    )
                    drawLine(
                        color = if (major) onSurface.copy(alpha = .58f) else outline.copy(alpha = .35f),
                        start = start,
                        end = end,
                        strokeWidth = if (major) 2.dp.toPx() else 1.dp.toPx(),
                        cap = StrokeCap.Round,
                    )
                }

                visiblePeriods.forEach { (start, end) ->
                    val span = (dayEnd - dayStart).coerceAtLeast(1L).toFloat()
                    val startFraction = ((start - dayStart).toFloat() / span).coerceIn(0f, 1f)
                    val endFraction = ((end - dayStart).toFloat() / span).coerceIn(0f, 1f)
                    val sweep = ((endFraction - startFraction) * 360f).coerceAtLeast(1.2f)
                    drawArc(
                        color = primary,
                        startAngle = -90f + startFraction * 360f,
                        sweepAngle = sweep,
                        useCenter = false,
                        topLeft = arcTopLeft,
                        size = arcSize,
                        style = Stroke(width = 12.dp.toPx(), cap = StrokeCap.Round),
                    )
                }

                listOf(0, 3, 6, 9, 12, 15, 18, 21).forEach { hour ->
                    val angle = Math.toRadians((hour * 15.0) - 90.0)
                    val labelRadius = radius - 23.dp.toPx()
                    val x = center.x + cos(angle).toFloat() * labelRadius
                    val y = center.y + sin(angle).toFloat() * labelRadius + textSizePx * .35f
                    drawContext.canvas.nativeCanvas.drawText(hour.toString().padStart(2, '0'), x, y, labelPaint)
                }

                drawCircle(color = primary, radius = 4.5.dp.toPx(), center = center)
                val currentFraction = ((now.coerceIn(dayStart, dayEnd) - dayStart).toFloat() / (dayEnd - dayStart).coerceAtLeast(1L).toFloat())
                val currentAngle = Math.toRadians((currentFraction * 360f - 90f).toDouble())
                drawLine(
                    color = onSurface.copy(alpha = .75f),
                    start = center,
                    end = androidx.compose.ui.geometry.Offset(
                        center.x + cos(currentAngle).toFloat() * (radius - 36.dp.toPx()),
                        center.y + sin(currentAngle).toFloat() * (radius - 36.dp.toPx()),
                    ),
                    strokeWidth = 2.dp.toPx(),
                    cap = StrokeCap.Round,
                )
            }
        }
    }
}

@Composable
private fun SummaryStat(label: String, value: String, accent: Color, modifier: Modifier = Modifier) {'''
    if marker2 not in text:
        raise SystemExit("Summary marker not found: refusing to build the wrong UI source")
    text = text.replace(marker2, clock, 1)

home.write_text(text, encoding="utf-8")

b = build.read_text(encoding="utf-8")
import re
b = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 11', b, count=1)
b = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "3.5.1"', b, count=1)
build.write_text(b, encoding="utf-8")

# Guardrails: fail CI if the expected corrections are absent.
checks = {
    "no-target refresh": "Aucune cible sélectionnée à actualiser.",
    "engine selector": "ObservationMode",
    "Hinozall": "HINOZALL_AWOKEN",
}
merged = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in root.rglob("*.kt"))
for label, needle in checks.items():
    if needle not in merged:
        raise SystemExit(f"Missing required correction: {label}")

manifest = (root / "app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
if 'android:supportsPictureInPicture="true"' not in manifest or 'android:resizeableActivity="true"' not in manifest:
    raise SystemExit("PiP manifest correction missing")

print("Prepared Hinozall Awoken 3.5.1 modern source with activity clock.")


# --- STRICT REBASE FROM USER'S LATEST "Le mega" ULTRA ---
# The public repository never contains signing material.  These two tiny patches
# first transform the old public CI source into the exact app/ tree verified
# against the user's latest Ultra, then apply only the requested 3.5.2 changes.
import base64, gzip, hashlib, subprocess\nP1_TAIL_B = """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"""\nP1_TAIL_A = """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"""

def apply_gz_patch(encoded: str, label: str) -> None:
    data = gzip.decompress(base64.b64decode(encoded))
    result = subprocess.run(
        ["patch", "-p1", "--batch", "--forward"],
        input=data,
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        raise SystemExit(f"{label} failed:\n" + result.stdout.decode("utf-8", "replace"))

apply_gz_patch("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", "strict Ultra rebase")
apply_gz_patch("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", "final 3.5.2 corrections")

expected = {
    "app/build.gradle.kts": "58f7310865f1da5613922decdf16c4688df54f4ea27c6cf8bff3e25fead43cac",
    "app/src/main/java/com/domniscian/app/MainActivity.kt": "6b225b52fd0a885889162fdaf6d3d8cb5f4069a8f0b2d51a367a58d19a299dd6",
    "app/src/main/java/com/domniscian/app/MainViewModel.kt": "2ada81827da1bd7e5fa3ceb798b0847d670b752a21eed7878d02a9cdcfc11db4",
    "app/src/main/java/com/domniscian/app/background/PresenceMonitorService.kt": "d4b25255d0436809789ba822de798113485e5ca58fcdbb6aa922ace3290e7657",
    "app/src/main/java/com/domniscian/app/ui/screens/HomeScreen.kt": "1e079446d61ce46ae993f838a9ae744aa6d0f93e002d010892b42b60b643406b",
    "app/src/main/java/com/domniscian/app/ui/screens/MessagesScreen.kt": "d29a6173aa0b771e67b33faf1d0ce51ab0e452ca0d8f7e54b0e660b1c71b6d8b",
    "app/src/main/java/com/domniscian/app/ui/screens/SettingsScreen.kt": "c73ef65bd434a9b36151f6cb8461186f91b87d8ae9d7ddc29a16f51326d2586d",
    "app/src/main/java/com/domniscian/app/ui/screens/AnalyticsScreen.kt": "90b32c822779cfad184aefa045a3145168b036a222d30a8a1f4f716392f94e5a",
    "app/src/main/AndroidManifest.xml": "f125850d50ab79a751d69589c83e27afc73bc1b21343ebe825d676e62a30acee",
}
for rel, wanted in expected.items():
    got = hashlib.sha256((root / rel).read_bytes()).hexdigest()
    if got != wanted:
        raise SystemExit(f"Wrong source after rebase: {rel} {got} != {wanted}")

merged = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in root.rglob("*.kt"))
for needle in [
    "Aucune cible sélectionnée à actualiser.",
    "ObservationMode.HINOZALL_AWOKEN",
    "ObservationMode.DOMNISCIAN",
    "DOM-526", "DOM-527", "DOM-528",
    "HorizontalPager",
    "ActivityDayClock",
    "activityClockView",
]:
    if needle not in merged:
        raise SystemExit("Missing final correction: " + needle)

print("Strict latest-Ultra rebase verified; Hinozall Awoken 3.5.2 ready to compile.")
