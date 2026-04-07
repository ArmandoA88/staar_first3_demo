param(
    [string]$OutputCsv = "C:\Users\laptop\Desktop\staar_first3_demo\Blooket\Grade3_Math_STAAR_Blooket_300.csv"
)

$ErrorActionPreference = "Stop"

$outputDirectory = Split-Path -Path $OutputCsv -Parent
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}

$questions = [System.Collections.Generic.List[object]]::new()

function Format-Whole {
    param($Number)
    $value = [int](@($Number)[0])
    return ('{0:N0}' -f $value)
}

function Format-Money {
    param($Cents)
    $value = [int](@($Cents)[0])
    return ('$' + ('{0:N2}' -f ($value / 100.0)))
}

function Format-Fraction {
    param(
        $Numerator,
        $Denominator
    )
    $num = [int](@($Numerator)[0])
    $den = [int](@($Denominator)[0])
    return "$num/$den"
}

function Convert-ToCsvField {
    param([AllowNull()][string]$Value)
    $text = if ($null -eq $Value) { "" } else { $Value }
    return '"' + ($text -replace '"', '""') + '"'
}

function Get-ExpandedNotation {
    param([int]$Number)

    $digits = [string]$Number
    $parts = New-Object System.Collections.Generic.List[string]

    for ($i = 0; $i -lt $digits.Length; $i++) {
        $digit = [int][string]$digits[$i]
        if ($digit -ne 0) {
            $power = $digits.Length - $i - 1
            $placeValue = $digit * [int][Math]::Pow(10, $power)
            $parts.Add((Format-Whole $placeValue))
        }
    }

    return ($parts -join " + ")
}

function Get-UniqueIntOptions {
    param(
        [int]$Correct,
        [int[]]$Candidates
    )

    $Correct = [int](@($Correct)[0])
    $Candidates = @($Candidates | ForEach-Object { [int]$_ })

    $options = [System.Collections.Generic.List[int]]::new()
    foreach ($candidate in $Candidates) {
        if ($candidate -ge 0 -and $candidate -ne $Correct -and -not $options.Contains($candidate)) {
            $options.Add($candidate)
        }
    }

    $step = [int][Math]::Max(2, [Math]::Floor([Math]::Max(10, [Math]::Abs($Correct)) / 10))
    while ($options.Count -lt 3) {
        $fallbacks = @(
            ([int]($Correct + $step)),
            ([int][Math]::Max(0, $Correct - $step)),
            ([int]($Correct + ($step + 3))),
            ([int][Math]::Max(0, $Correct - ($step + 3))),
            ([int]($Correct + 1)),
            ([int][Math]::Max(0, $Correct - 1))
        )
        foreach ($candidate in $fallbacks) {
            if ($candidate -ne $Correct -and -not $options.Contains($candidate)) {
                $options.Add($candidate)
            }
            if ($options.Count -ge 3) {
                break
            }
        }
        $step += 7
    }

    return @($Correct, $options[0], $options[1], $options[2])
}

function Add-Question {
    param(
        [Parameter(Mandatory = $true)]
        [string]$QuestionText,
        [Parameter(Mandatory = $true)]
        [string[]]$Answers,
        [Parameter(Mandatory = $true)]
        [int]$CorrectIndex,
        [int]$TimeLimit = 35
    )

    if ($Answers.Count -ne 4) {
        throw "Each question must have exactly 4 answers. Count=$($Answers.Count). Question=$QuestionText"
    }

    $answerObjects = @()
    for ($i = 0; $i -lt $Answers.Count; $i++) {
        $answerObjects += [pscustomobject]@{
            Text      = [string]$Answers[$i]
            IsCorrect = (($i + 1) -eq $CorrectIndex)
        }
    }

    $shuffled = @($answerObjects | Sort-Object { Get-Random })
    $newCorrect = 1
    for ($i = 0; $i -lt $shuffled.Count; $i++) {
        if ($shuffled[$i].IsCorrect) {
            $newCorrect = $i + 1
            break
        }
    }

    $questions.Add([pscustomobject]@{
        question = $QuestionText
        answers  = @($shuffled | ForEach-Object { $_.Text })
        correct  = [string]$newCorrect
        time     = $TimeLimit
    }) | Out-Null
}

function Add-IntegerQuestion {
    param(
        [string]$QuestionText,
        [int]$Correct,
        [int[]]$CandidateDistractors,
        [int]$TimeLimit = 35,
        [string]$Suffix = ""
    )

    $values = Get-UniqueIntOptions -Correct $Correct -Candidates $CandidateDistractors
    $answerStrings = @(
        $values | ForEach-Object {
            $formatted = Format-Whole $_
            if ($Suffix) { "$formatted $Suffix" } else { $formatted }
        }
    )

    Add-Question -QuestionText $QuestionText -Answers $answerStrings -CorrectIndex 1 -TimeLimit $TimeLimit
}

function Add-MoneyQuestion {
    param(
        [string]$QuestionText,
        [int]$CorrectCents,
        [int[]]$CandidateDistractors,
        [int]$TimeLimit = 35
    )

    $values = Get-UniqueIntOptions -Correct $CorrectCents -Candidates $CandidateDistractors
    $answerStrings = @($values | ForEach-Object { Format-Money $_ })
    Add-Question -QuestionText $QuestionText -Answers $answerStrings -CorrectIndex 1 -TimeLimit $TimeLimit
}

function Add-FractionQuestion {
    param(
        [string]$QuestionText,
        [string]$Correct,
        [string[]]$Distractors,
        [int]$TimeLimit = 35
    )

    $answers = [System.Collections.Generic.List[string]]::new()
    $answers.Add($Correct)
    foreach ($distractor in $Distractors) {
        if ($distractor -ne $Correct -and -not $answers.Contains($distractor)) {
            $answers.Add($distractor)
        }
    }

    if ($answers.Count -lt 4) {
        for ($den = 2; $den -le 10 -and $answers.Count -lt 4; $den++) {
            for ($num = 1; $num -le $den -and $answers.Count -lt 4; $num++) {
                $candidate = "$num/$den"
                if ($candidate -ne $Correct -and -not $answers.Contains($candidate)) {
                    $answers.Add($candidate)
                }
            }
        }
    }

    if ($answers.Count -ne 4) {
        throw "Fraction question must resolve to 4 unique answers. Question=$QuestionText Answers=$($answers -join '; ')"
    }

    Add-Question -QuestionText $QuestionText -Answers @($answers) -CorrectIndex 1 -TimeLimit $TimeLimit
}

function Get-GreatestCommonDivisor {
    param(
        [int]$A,
        [int]$B
    )

    $x = [Math]::Abs($A)
    $y = [Math]::Abs($B)
    while ($y -ne 0) {
        $temp = $x % $y
        $x = $y
        $y = $temp
    }

    return [Math]::Max(1, $x)
}

function Get-UniqueRandomNumbers {
    param(
        [int]$Count,
        [int]$Minimum,
        [int]$Maximum,
        [int[]]$Exclude = @()
    )

    $values = [System.Collections.Generic.List[int]]::new()
    while ($values.Count -lt $Count) {
        $candidate = Get-Random -Minimum $Minimum -Maximum $Maximum
        if (-not $values.Contains($candidate) -and -not ($Exclude -contains $candidate)) {
            $values.Add($candidate)
        }
    }

    return @($values)
}

function Add-PlaceValueQuestions {
    for ($i = 0; $i -lt 10; $i++) {
        $number = Get-Random -Minimum 12000 -Maximum 99999
        $expanded = Get-ExpandedNotation -Number $number
        $d1 = $number + ((Get-Random -Minimum 1 -Maximum 5) * 10)
        $d2 = $number - ((Get-Random -Minimum 1 -Maximum 5) * 100)
        $d3 = $number + ((Get-Random -Minimum 1 -Maximum 7) * 1000)
        Add-IntegerQuestion `
            -QuestionText "Concept: Expanded notation shows a number as the sum of each digit's place value. Question: Which number is written as ${expanded}?" `
            -Correct $number `
            -CandidateDistractors @($d1, $d2, $d3) `
            -TimeLimit 30
    }

    for ($i = 0; $i -lt 10; $i++) {
        $digits = @(1,2,3,4,5,6,7,8,9) | Sort-Object { Get-Random } | Select-Object -First 5
        $number = [int](($digits -join ''))
        $placeIndex = Get-Random -Minimum 0 -Maximum 5
        $digit = $digits[$placeIndex]
        $placePower = 4 - $placeIndex
        $value = $digit * [int][Math]::Pow(10, $placePower)
        $d1 = $digit
        $d2 = $digit * [int][Math]::Pow(10, [Math]::Max(0, $placePower - 1))
        $d3 = $digit * [int][Math]::Pow(10, [Math]::Min(4, $placePower + 1))
        $numberText = Format-Whole $number
        Add-IntegerQuestion `
            -QuestionText "Concept: The value of a digit depends on its place. Question: In ${numberText}, what is the value of the digit ${digit}?" `
            -Correct $value `
            -CandidateDistractors @($d1, $d2, $d3) `
            -TimeLimit 30
    }

    for ($i = 0; $i -lt 5; $i++) {
        $choices = @(Get-UniqueRandomNumbers -Count 4 -Minimum 1000 -Maximum 9999)
        $correct = ($choices | Measure-Object -Maximum).Maximum
        $answers = @($choices | ForEach-Object { Format-Whole $_ })
        $correctIndex = [Array]::IndexOf($choices, $correct) + 1
        Add-Question `
            -QuestionText "Concept: Comparing numbers means deciding which has the greatest or least value. Question: Which number is greatest?" `
            -Answers $answers `
            -CorrectIndex $correctIndex `
            -TimeLimit 25
    }

    for ($i = 0; $i -lt 5; $i++) {
        $choices = @(Get-UniqueRandomNumbers -Count 4 -Minimum 1000 -Maximum 9999)
        $correct = ($choices | Measure-Object -Minimum).Minimum
        $answers = @($choices | ForEach-Object { Format-Whole $_ })
        $correctIndex = [Array]::IndexOf($choices, $correct) + 1
        Add-Question `
            -QuestionText "Concept: Comparing numbers means deciding which has the greatest or least value. Question: Which number is least?" `
            -Answers $answers `
            -CorrectIndex $correctIndex `
            -TimeLimit 25
    }

    for ($i = 0; $i -lt 5; $i++) {
        $number = Get-Random -Minimum 120 -Maximum 989
        $rounded = [int]([Math]::Round($number / 10.0, 0, [System.MidpointRounding]::AwayFromZero) * 10)
        $numberText = Format-Whole $number
        Add-IntegerQuestion `
            -QuestionText "Concept: Rounding to the nearest 10 means finding the closest multiple of 10. Question: What is $numberText rounded to the nearest 10?" `
            -Correct $rounded `
            -CandidateDistractors @(($rounded + 10), ([Math]::Max(0, $rounded - 10)), ($number)) `
            -TimeLimit 25
    }

    for ($i = 0; $i -lt 5; $i++) {
        $number = Get-Random -Minimum 150 -Maximum 9950
        $rounded = [int]([Math]::Round($number / 100.0, 0, [System.MidpointRounding]::AwayFromZero) * 100)
        $numberText = Format-Whole $number
        Add-IntegerQuestion `
            -QuestionText "Concept: Rounding to the nearest 100 means finding the closest multiple of 100. Question: What is $numberText rounded to the nearest 100?" `
            -Correct $rounded `
            -CandidateDistractors @(($rounded + 100), ([Math]::Max(0, $rounded - 100)), ([int]([Math]::Round($number / 10.0, 0, [System.MidpointRounding]::AwayFromZero) * 10))) `
            -TimeLimit 25
    }

    for ($i = 0; $i -lt 5; $i++) {
        $base = (Get-Random -Minimum 3 -Maximum 11) * 10
        $correct = Get-Random -Minimum ($base + 1) -Maximum ($base + 9)
        $wrongLow = Get-Random -Minimum ($base - 9) -Maximum $base
        $highChoices = @(Get-UniqueRandomNumbers -Count 2 -Minimum ($base + 10) -Maximum ($base + 20))
        $baseText = Format-Whole $base
        $upperText = Format-Whole ($base + 10)
        $answers = @(
            (Format-Whole $correct),
            (Format-Whole $wrongLow),
            (Format-Whole $highChoices[0]),
            (Format-Whole $highChoices[1])
        )
        Add-Question `
            -QuestionText "Concept: A number between two multiples is greater than the smaller multiple and less than the larger multiple. Question: Which number is between ${baseText} and ${upperText}?" `
            -Answers $answers `
            -CorrectIndex 1 `
            -TimeLimit 25
    }

    for ($i = 0; $i -lt 3; $i++) {
        $base = (Get-Random -Minimum 2 -Maximum 10) * 100
        $correct = Get-Random -Minimum ($base + 1) -Maximum ($base + 99)
        $highChoices = @(Get-UniqueRandomNumbers -Count 2 -Minimum ($base + 100) -Maximum ($base + 200))
        $baseText = Format-Whole $base
        $upperText = Format-Whole ($base + 100)
        $answers = @(
            (Format-Whole $correct),
            (Format-Whole (Get-Random -Minimum ($base - 99) -Maximum $base)),
            (Format-Whole $highChoices[0]),
            (Format-Whole $highChoices[1])
        )
        Add-Question `
            -QuestionText "Concept: A number between two multiples of 100 is greater than the smaller hundred and less than the larger hundred. Question: Which number is between ${baseText} and ${upperText}?" `
            -Answers $answers `
            -CorrectIndex 1 `
            -TimeLimit 25
    }

    for ($i = 0; $i -lt 2; $i++) {
        $base = (Get-Random -Minimum 2 -Maximum 8) * 1000
        $correct = Get-Random -Minimum ($base + 1) -Maximum ($base + 999)
        $highChoices = @(Get-UniqueRandomNumbers -Count 2 -Minimum ($base + 1000) -Maximum ($base + 2000))
        $baseText = Format-Whole $base
        $upperText = Format-Whole ($base + 1000)
        $answers = @(
            (Format-Whole $correct),
            (Format-Whole (Get-Random -Minimum ($base - 999) -Maximum $base)),
            (Format-Whole $highChoices[0]),
            (Format-Whole $highChoices[1])
        )
        Add-Question `
            -QuestionText "Concept: A number between two multiples of 1,000 is greater than the smaller thousand and less than the larger thousand. Question: Which number is between ${baseText} and ${upperText}?" `
            -Answers $answers `
            -CorrectIndex 1 `
            -TimeLimit 25
    }
}

function Add-AdditionSubtractionQuestions {
    $additionContexts = @("stickers", "books", "marbles", "crayons", "shells", "beans", "pencils", "cards", "beads", "buttons")
    for ($i = 0; $i -lt 10; $i++) {
        $a = Get-Random -Minimum 120 -Maximum 690
        $b = Get-Random -Minimum 115 -Maximum 305
        $total = $a + $b
        $item = $additionContexts[$i]
        $aText = Format-Whole $a
        $bText = Format-Whole $b
        Add-IntegerQuestion `
            -QuestionText "Concept: Addition combines amounts to find a total. Question: A class collected $aText $item on Monday and $bText more on Tuesday. How many $item did the class collect in all?" `
            -Correct $total `
            -CandidateDistractors @(($a + $b + 10), ([Math]::Abs($a - $b)), ($a + $b - 10)) `
            -TimeLimit 35
    }

    $subtractionContexts = @("tickets", "flowers", "cans", "markers", "blocks", "papers", "toy cars", "cookies", "erasers", "ribbons")
    for ($i = 0; $i -lt 10; $i++) {
        $start = Get-Random -Minimum 320 -Maximum 980
        $taken = Get-Random -Minimum 110 -Maximum 290
        $left = $start - $taken
        $item = $subtractionContexts[$i]
        $startText = Format-Whole $start
        $takenText = Format-Whole $taken
        Add-IntegerQuestion `
            -QuestionText "Concept: Subtraction finds how many are left after some are taken away. Question: A box had $startText $item. Then $takenText were used. How many $item are left?" `
            -Correct $left `
            -CandidateDistractors @(($start + $taken), ($taken), ($left + 10)) `
            -TimeLimit 35
    }

    $twoStepContexts = @(
        @{ Item = "pencils"; First = "bought"; Second = "gave away" },
        @{ Item = "stickers"; First = "found"; Second = "shared" },
        @{ Item = "books"; First = "checked out"; Second = "returned" },
        @{ Item = "marbles"; First = "won"; Second = "lost" },
        @{ Item = "apples"; First = "picked"; Second = "used" },
        @{ Item = "shells"; First = "collected"; Second = "gave away" },
        @{ Item = "cards"; First = "earned"; Second = "used" },
        @{ Item = "beads"; First = "added"; Second = "dropped" },
        @{ Item = "buttons"; First = "sorted"; Second = "set aside" },
        @{ Item = "papers"; First = "stacked"; Second = "recycled" }
    )
    for ($i = 0; $i -lt 10; $i++) {
        $start = Get-Random -Minimum 150 -Maximum 500
        $add = Get-Random -Minimum 40 -Maximum 180
        $sub = Get-Random -Minimum 30 -Maximum 140
        $correct = $start + $add - $sub
        $context = $twoStepContexts[$i]
        $startText = Format-Whole $start
        $addText = Format-Whole $add
        $subText = Format-Whole $sub
        Add-IntegerQuestion `
            -QuestionText "Concept: A two-step problem may need addition and subtraction in order. Question: Mia had $startText $($context.Item). She $($context.First) $addText more and then $($context.Second) $subText. How many $($context.Item) does she have now?" `
            -Correct $correct `
            -CandidateDistractors @(($start + $add + $sub), ($start - $sub), ($start + $add)) `
            -TimeLimit 40
    }

    for ($i = 0; $i -lt 10; $i++) {
        $a = Get-Random -Minimum 120 -Maximum 895
        $b = Get-Random -Minimum 115 -Maximum 795
        $roundA = [int]([Math]::Round($a / 10.0, 0, [System.MidpointRounding]::AwayFromZero) * 10)
        $roundB = [int]([Math]::Round($b / 10.0, 0, [System.MidpointRounding]::AwayFromZero) * 10)
        $estimate = $roundA + $roundB
        $aText = Format-Whole $a
        $bText = Format-Whole $b
        Add-IntegerQuestion `
            -QuestionText "Concept: Estimating uses rounded numbers to find a close answer. Question: Which is the best estimate for ${aText} + ${bText}?" `
            -Correct $estimate `
            -CandidateDistractors @(($a + $b), ([Math]::Abs($roundA - $roundB)), ($estimate + 100)) `
            -TimeLimit 30
    }

    $moneySetups = @(
        @{ Dollars = 3; Quarters = 2; Dimes = 1; Nickels = 0; Pennies = 4 },
        @{ Dollars = 4; Quarters = 1; Dimes = 3; Nickels = 1; Pennies = 2 },
        @{ Dollars = 2; Quarters = 3; Dimes = 0; Nickels = 2; Pennies = 1 },
        @{ Dollars = 5; Quarters = 0; Dimes = 2; Nickels = 2; Pennies = 5 },
        @{ Dollars = 1; Quarters = 3; Dimes = 2; Nickels = 0; Pennies = 3 },
        @{ Dollars = 6; Quarters = 1; Dimes = 1; Nickels = 1; Pennies = 0 },
        @{ Dollars = 2; Quarters = 2; Dimes = 2; Nickels = 2; Pennies = 2 },
        @{ Dollars = 3; Quarters = 1; Dimes = 0; Nickels = 3; Pennies = 4 },
        @{ Dollars = 4; Quarters = 2; Dimes = 2; Nickels = 1; Pennies = 1 },
        @{ Dollars = 5; Quarters = 3; Dimes = 1; Nickels = 0; Pennies = 2 }
    )
    for ($i = 0; $i -lt 10; $i++) {
        $setup = $moneySetups[$i]
        $correct = ($setup.Dollars * 100) + ($setup.Quarters * 25) + ($setup.Dimes * 10) + ($setup.Nickels * 5) + $setup.Pennies
        Add-MoneyQuestion `
            -QuestionText "Concept: The value of money is found by adding the value of each bill and coin. Question: What is the total value of $($setup.Dollars) one-dollar bills, $($setup.Quarters) quarters, $($setup.Dimes) dimes, $($setup.Nickels) nickels, and $($setup.Pennies) pennies?" `
            -CorrectCents $correct `
            -CandidateDistractors @(($correct + 10), ($correct - 10), ($setup.Dollars + $setup.Quarters + $setup.Dimes + $setup.Nickels + $setup.Pennies)) `
            -TimeLimit 35
    }
}

function Add-MultiplicationDivisionQuestions {
    $groupItems = @("stickers", "marbles", "toy cars", "books", "crayons", "shells", "balloons", "cards", "beads", "flowers", "pencils", "cookies")
    for ($i = 0; $i -lt 12; $i++) {
        $groups = Get-Random -Minimum 2 -Maximum 10
        $each = Get-Random -Minimum 2 -Maximum 10
        $total = $groups * $each
        $item = $groupItems[$i]
        Add-IntegerQuestion `
            -QuestionText "Concept: Multiplication finds the total in equal groups. Question: There are $groups groups with $each $item in each group. How many $item are there in all?" `
            -Correct $total `
            -CandidateDistractors @(($groups + $each), ($total + $each), ([Math]::Abs($groups - $each))) `
            -TimeLimit 35
    }

    for ($i = 0; $i -lt 8; $i++) {
        $rows = Get-Random -Minimum 2 -Maximum 8
        $cols = Get-Random -Minimum 2 -Maximum 9
        $product = $rows * $cols
        $correct = "$rows x $cols = $product"
        $answers = @(
            $correct,
            "$rows + $cols = $product",
            "$rows x $cols = $($product + $rows)",
            "$rows + $cols = $($rows + $cols)"
        )
        Add-Question `
            -QuestionText "Concept: An array uses rows and columns to show multiplication. Question: An array has $rows rows with $cols objects in each row. Which equation matches the array?" `
            -Answers $answers `
            -CorrectIndex 1 `
            -TimeLimit 35
    }

    $shareItems = @("crackers", "markers", "shells", "apples", "cards", "cubes", "flowers", "buttons", "erasers", "beads")
    for ($i = 0; $i -lt 10; $i++) {
        $groups = Get-Random -Minimum 2 -Maximum 9
        $each = Get-Random -Minimum 2 -Maximum 10
        $total = $groups * $each
        $item = $shareItems[$i]
        Add-IntegerQuestion `
            -QuestionText "Concept: Division can show equal sharing. Question: $total $item are shared equally among $groups students. How many $item does each student get?" `
            -Correct $each `
            -CandidateDistractors @(($total), ($groups), ($each + 2)) `
            -TimeLimit 35
    }

    for ($i = 0; $i -lt 10; $i++) {
        $factor1 = Get-Random -Minimum 2 -Maximum 10
        $factor2 = Get-Random -Minimum 2 -Maximum 10
        $product = $factor1 * $factor2
        if ($i % 2 -eq 0) {
            Add-IntegerQuestion `
                -QuestionText "Concept: A missing factor can be found using multiplication facts. Question: What number makes the equation true? $factor1 x __ = $product" `
                -Correct $factor2 `
                -CandidateDistractors @(($factor1), ($product), ($factor2 + 1)) `
                -TimeLimit 30
        }
        else {
            Add-IntegerQuestion `
                -QuestionText "Concept: A missing factor can be found using multiplication facts. Question: What number makes the equation true? __ x $factor2 = $product" `
                -Correct $factor1 `
                -CandidateDistractors @(($factor2), ($product), ($factor1 + 1)) `
                -TimeLimit 30
        }
    }

    $comparisonItems = @("stickers", "books", "toy cars", "marbles", "cookies", "shells", "baseball cards", "flowers")
    for ($i = 0; $i -lt 8; $i++) {
        $baseAmount = Get-Random -Minimum 2 -Maximum 10
        $times = Get-Random -Minimum 2 -Maximum 6
        $correct = $baseAmount * $times
        $item = $comparisonItems[$i]
        Add-IntegerQuestion `
            -QuestionText "Concept: A multiplicative comparison tells how many times as many one amount is as another. Question: Leo has $baseAmount $item. Ava has $times times as many $item as Leo. How many $item does Ava have?" `
            -Correct $correct `
            -CandidateDistractors @(($baseAmount + $times), ($baseAmount * ($times + 1)), ($times)) `
            -TimeLimit 35
    }

    for ($i = 0; $i -lt 3; $i++) {
        $answers = @(2, 4, 7, 9) | Sort-Object { Get-Random }
        $correctIndex = if ($answers[0] % 2 -eq 0) { 1 } elseif ($answers[1] % 2 -eq 0) { 2 } elseif ($answers[2] % 2 -eq 0) { 3 } else { 4 }
        Add-Question `
            -QuestionText "Concept: An even number can be split into 2 equal groups with none left over. Question: Which number is even?" `
            -Answers @($answers | ForEach-Object { [string]$_ }) `
            -CorrectIndex $correctIndex `
            -TimeLimit 20
    }

    for ($i = 0; $i -lt 3; $i++) {
        $answers = @(3, 5, 8, 12) | Sort-Object { Get-Random }
        $correctIndex = if ($answers[0] % 2 -eq 1) { 1 } elseif ($answers[1] % 2 -eq 1) { 2 } elseif ($answers[2] % 2 -eq 1) { 3 } else { 4 }
        Add-Question `
            -QuestionText "Concept: An odd number has 1 left over when it is split into 2 equal groups. Question: Which number is odd?" `
            -Answers @($answers | ForEach-Object { [string]$_ }) `
            -CorrectIndex $correctIndex `
            -TimeLimit 20
    }

    for ($i = 0; $i -lt 6; $i++) {
        $rule = Get-Random -Minimum 2 -Maximum 10
        $input1 = Get-Random -Minimum 2 -Maximum 7
        $input2 = $input1 + 2
        $input3 = $input1 + 4
        $newInput = $input1 + 5
        $correct = $newInput * $rule
        Add-IntegerQuestion `
            -QuestionText "Concept: A number-pair table can show a rule between input and output. Question: A table follows the rule multiply by $rule. If the input numbers $input1, $input2, and $input3 have outputs $($input1 * $rule), $($input2 * $rule), and $($input3 * $rule), what is the output for input ${newInput}?" `
            -Correct $correct `
            -CandidateDistractors @(($newInput + $rule), ($newInput * ($rule + 1)), ($correct - $rule)) `
            -TimeLimit 35
    }
}

function Add-FractionQuestions {
    for ($i = 0; $i -lt 10; $i++) {
        $denominator = Get-Random -Minimum 2 -Maximum 9
        Add-FractionQuestion `
            -QuestionText "Concept: A unit fraction names 1 equal part of a whole. Question: Which fraction names 1 part when a whole is divided into $denominator equal parts?" `
            -Correct (Format-Fraction -Numerator 1 -Denominator $denominator) `
            -Distractors @(
                (Format-Fraction -Numerator 2 -Denominator $denominator),
                (Format-Fraction -Numerator 1 -Denominator ($denominator + 1)),
                (Format-Fraction -Numerator $denominator -Denominator $denominator)
            ) `
            -TimeLimit 30
    }

    for ($i = 0; $i -lt 10; $i++) {
        $denominator = Get-Random -Minimum 3 -Maximum 9
        $numerator = Get-Random -Minimum 1 -Maximum $denominator
        $wrong1 = [Math]::Min($denominator, $numerator + 1)
        if ($wrong1 -eq $numerator) { $wrong1 = [Math]::Max(1, $numerator - 1) }
        Add-FractionQuestion `
            -QuestionText "Concept: A fraction tells how many equal parts are being described. Question: A shape is split into $denominator equal parts and $numerator parts are shaded. Which fraction names the shaded part?" `
            -Correct (Format-Fraction -Numerator $numerator -Denominator $denominator) `
            -Distractors @(
                (Format-Fraction -Numerator $wrong1 -Denominator $denominator),
                (Format-Fraction -Numerator $numerator -Denominator ($denominator + 1)),
                (Format-Fraction -Numerator $denominator -Denominator $numerator)
            ) `
            -TimeLimit 30
    }

    for ($i = 0; $i -lt 5; $i++) {
        $denominator = Get-Random -Minimum 2 -Maximum 9
        $mark = Get-Random -Minimum 1 -Maximum $denominator
        $wrong1 = [Math]::Min($denominator, $mark + 1)
        if ($wrong1 -eq $mark) { $wrong1 = [Math]::Max(1, $mark - 1) }
        Add-FractionQuestion `
            -QuestionText "Concept: Fractions can be located on a number line between 0 and 1. Question: A number line from 0 to 1 is divided into $denominator equal parts. What fraction names the $mark$(if ($mark -eq 1) { 'st' } elseif ($mark -eq 2) { 'nd' } elseif ($mark -eq 3) { 'rd' } else { 'th' }) mark after 0?" `
            -Correct (Format-Fraction -Numerator $mark -Denominator $denominator) `
            -Distractors @(
                (Format-Fraction -Numerator $wrong1 -Denominator $denominator),
                (Format-Fraction -Numerator 1 -Denominator $denominator),
                (Format-Fraction -Numerator $denominator -Denominator $denominator)
            ) `
            -TimeLimit 30
    }

    $equivalentPairs = @(
        @{ BaseN = 1; BaseD = 2; EqN = 2; EqD = 4; W1 = "2/3"; W2 = "3/4" },
        @{ BaseN = 1; BaseD = 3; EqN = 2; EqD = 6; W1 = "1/6"; W2 = "3/6" },
        @{ BaseN = 2; BaseD = 3; EqN = 4; EqD = 6; W1 = "3/6"; W2 = "2/6" },
        @{ BaseN = 1; BaseD = 4; EqN = 2; EqD = 8; W1 = "1/8"; W2 = "3/8" },
        @{ BaseN = 3; BaseD = 4; EqN = 6; EqD = 8; W1 = "4/8"; W2 = "5/8" }
    )
    foreach ($pair in $equivalentPairs) {
        Add-FractionQuestion `
            -QuestionText "Concept: Equivalent fractions name the same amount even when the numbers look different. Question: Which fraction is equivalent to $($pair.BaseN)/$($pair.BaseD)?" `
            -Correct "$($pair.EqN)/$($pair.EqD)" `
            -Distractors @($pair.W1, $pair.W2, "$($pair.BaseN)/$($pair.EqD)") `
            -TimeLimit 30
    }

    for ($i = 0; $i -lt 5; $i++) {
        $denominator = Get-Random -Minimum 3 -Maximum 9
        $n1 = Get-Random -Minimum 1 -Maximum ($denominator - 1)
        $n2 = Get-Random -Minimum ($n1 + 1) -Maximum $denominator
        Add-FractionQuestion `
            -QuestionText "Concept: Fractions with the same denominator can be compared by their numerators. Question: Which fraction is greater?" `
            -Correct (Format-Fraction -Numerator $n2 -Denominator $denominator) `
            -Distractors @(
                (Format-Fraction -Numerator $n1 -Denominator $denominator),
                (Format-Fraction -Numerator 1 -Denominator ($denominator + 1)),
                (Format-Fraction -Numerator $denominator -Denominator $denominator)
            ) `
            -TimeLimit 25
    }

    for ($i = 0; $i -lt 5; $i++) {
        $numerator = Get-Random -Minimum 1 -Maximum 4
        $dSmall = Get-Random -Minimum ($numerator + 1) -Maximum 6
        $dLarge = Get-Random -Minimum ($dSmall + 1) -Maximum 10
        Add-FractionQuestion `
            -QuestionText "Concept: When fractions have the same numerator, the fraction with the smaller denominator is greater. Question: Which fraction is greater?" `
            -Correct (Format-Fraction -Numerator $numerator -Denominator $dSmall) `
            -Distractors @(
                (Format-Fraction -Numerator $numerator -Denominator $dLarge),
                (Format-Fraction -Numerator ($numerator + 1) -Denominator $dLarge),
                (Format-Fraction -Numerator 1 -Denominator $dSmall)
            ) `
            -TimeLimit 25
    }

    for ($i = 0; $i -lt 5; $i++) {
        $friends = Get-Random -Minimum 2 -Maximum 9
        Add-FractionQuestion `
            -QuestionText "Concept: Sharing one whole equally means each share is a unit fraction. Question: One sandwich is shared equally among $friends students. What fraction of the sandwich does each student get?" `
            -Correct (Format-Fraction -Numerator 1 -Denominator $friends) `
            -Distractors @(
                (Format-Fraction -Numerator $friends -Denominator $friends),
                (Format-Fraction -Numerator 2 -Denominator $friends),
                (Format-Fraction -Numerator 1 -Denominator ($friends + 1))
            ) `
            -TimeLimit 30
    }

    $decomposeSet = @(
        @{ Unit = "1/4"; Count = 3; Correct = "3/4"; Wrong1 = "2/4"; Wrong2 = "4/4"; Wrong3 = "1/3" },
        @{ Unit = "1/5"; Count = 4; Correct = "4/5"; Wrong1 = "5/5"; Wrong2 = "3/5"; Wrong3 = "1/4" },
        @{ Unit = "1/6"; Count = 2; Correct = "2/6"; Wrong1 = "3/6"; Wrong2 = "1/6"; Wrong3 = "2/5" },
        @{ Unit = "1/8"; Count = 5; Correct = "5/8"; Wrong1 = "4/8"; Wrong2 = "6/8"; Wrong3 = "1/5" },
        @{ Unit = "1/3"; Count = 2; Correct = "2/3"; Wrong1 = "1/3"; Wrong2 = "3/3"; Wrong3 = "2/4" }
    )
    foreach ($set in $decomposeSet) {
        $parts = @()
        for ($i = 0; $i -lt $set.Count; $i++) {
            $parts += $set.Unit
        }
        $sumText = $parts -join " + "
        Add-FractionQuestion `
            -QuestionText "Concept: Fractions can be built by joining unit fractions. Question: Which fraction is the same as ${sumText}?" `
            -Correct $set.Correct `
            -Distractors @($set.Wrong1, $set.Wrong2, $set.Wrong3) `
            -TimeLimit 30
    }
}

function Add-GeometryMeasurementQuestions {
    $threeDShapes = @("cube", "rectangular prism", "cone", "cylinder")
    $twoDShapes = @("triangle", "rectangle", "hexagon", "rhombus", "pentagon", "trapezoid")

    for ($i = 0; $i -lt 4; $i++) {
        $correct = $threeDShapes[$i]
        $wrongs = @($twoDShapes | Sort-Object { Get-Random } | Select-Object -First 3)
        Add-Question `
            -QuestionText "Concept: A 3D figure is solid and has length, width, and height. Question: Which shape is a 3D figure?" `
            -Answers @($correct, $wrongs[0], $wrongs[1], $wrongs[2]) `
            -CorrectIndex 1 `
            -TimeLimit 20
    }

    for ($i = 0; $i -lt 4; $i++) {
        $correct = $twoDShapes[$i]
        $wrongs = @($threeDShapes | Sort-Object { Get-Random } | Select-Object -First 3)
        Add-Question `
            -QuestionText "Concept: A 2D figure is flat and has only length and width. Question: Which shape is a 2D figure?" `
            -Answers @($correct, $wrongs[0], $wrongs[1], $wrongs[2]) `
            -CorrectIndex 1 `
            -TimeLimit 20
    }

    $quadCorrects = @("rectangle", "square", "rhombus", "trapezoid", "parallelogram")
    $nonQuads = @("triangle", "pentagon", "hexagon", "octagon")
    for ($i = 0; $i -lt 5; $i++) {
        $correct = $quadCorrects[$i]
        $wrongs = @($nonQuads | Sort-Object { Get-Random } | Select-Object -First 3)
        Add-Question `
            -QuestionText "Concept: A quadrilateral is a polygon with 4 sides. Question: Which shape is a quadrilateral?" `
            -Answers @($correct, $wrongs[0], $wrongs[1], $wrongs[2]) `
            -CorrectIndex 1 `
            -TimeLimit 20
    }

    for ($i = 0; $i -lt 3; $i++) {
        Add-IntegerQuestion `
            -QuestionText "Concept: A quadrilateral is a polygon with 4 sides. Question: How many sides does a quadrilateral have?" `
            -Correct 4 `
            -CandidateDistractors @(3, 5, 6) `
            -TimeLimit 20
    }

    for ($i = 0; $i -lt 8; $i++) {
        $length = Get-Random -Minimum 3 -Maximum 16
        $width = Get-Random -Minimum 2 -Maximum 12
        $perimeter = 2 * ($length + $width)
        Add-IntegerQuestion `
            -QuestionText "Concept: Perimeter is the distance around a figure. Question: What is the perimeter of a rectangle with side lengths $length units and $width units?" `
            -Correct $perimeter `
            -CandidateDistractors @(($length * $width), ($length + $width), ($perimeter + 2)) `
            -TimeLimit 30
    }

    for ($i = 0; $i -lt 4; $i++) {
        $s1 = Get-Random -Minimum 3 -Maximum 12
        $s2 = Get-Random -Minimum 3 -Maximum 12
        $s3 = Get-Random -Minimum 3 -Maximum 12
        $s4 = Get-Random -Minimum 3 -Maximum 12
        $perimeter = $s1 + $s2 + $s3 + $s4
        Add-IntegerQuestion `
            -QuestionText "Concept: Perimeter is found by adding the lengths of all sides. Question: A shape has side lengths of $s1 units, $s2 units, $s3 units, and $s4 units. What is its perimeter?" `
            -Correct $perimeter `
            -CandidateDistractors @(($s1 + $s2 + $s3), ($s1 * $s2), ($perimeter + 4)) `
            -TimeLimit 30
    }

    for ($i = 0; $i -lt 6; $i++) {
        $rows = Get-Random -Minimum 2 -Maximum 8
        $cols = Get-Random -Minimum 2 -Maximum 9
        $area = $rows * $cols
        Add-IntegerQuestion `
            -QuestionText "Concept: Area is the number of square units needed to cover a surface. Question: A rectangle has $rows rows of squares with $cols squares in each row. What is the area?" `
            -Correct $area `
            -CandidateDistractors @(($rows + $cols), ((2 * $rows) + (2 * $cols)), ($area + $rows)) `
            -TimeLimit 30
    }

    for ($i = 0; $i -lt 3; $i++) {
        $aRows = Get-Random -Minimum 2 -Maximum 5
        $aCols = Get-Random -Minimum 2 -Maximum 6
        $bRows = Get-Random -Minimum 2 -Maximum 5
        $bCols = Get-Random -Minimum 2 -Maximum 6
        $totalArea = ($aRows * $aCols) + ($bRows * $bCols)
        Add-IntegerQuestion `
            -QuestionText "Concept: The area of a composite figure can be found by adding the areas of smaller rectangles. Question: One rectangle has area $($aRows * $aCols) square units and a second rectangle has area $($bRows * $bCols) square units. What is the total area?" `
            -Correct $totalArea `
            -CandidateDistractors @(($aRows * $aCols), ($bRows * $bCols), ($totalArea + 4)) `
            -TimeLimit 35
    }

    $areaFractions = @(
        @{ Total = 8; Shaded = 3; Correct = "3/8"; W1 = "5/8"; W2 = "3/7"; W3 = "8/8" },
        @{ Total = 6; Shaded = 2; Correct = "2/6"; W1 = "4/6"; W2 = "2/5"; W3 = "6/6" },
        @{ Total = 10; Shaded = 7; Correct = "7/10"; W1 = "3/10"; W2 = "7/9"; W3 = "10/10" }
    )
    foreach ($set in $areaFractions) {
        Add-FractionQuestion `
            -QuestionText "Concept: Equal shares of area can be named with fractions. Question: A rectangle is divided into $($set.Total) equal squares. $($set.Shaded) squares are shaded. Which fraction of the area is shaded?" `
            -Correct $set.Correct `
            -Distractors @($set.W1, $set.W2, $set.W3) `
            -TimeLimit 30
    }

    for ($i = 0; $i -lt 5; $i++) {
        $startHour = Get-Random -Minimum 1 -Maximum 11
        $startMinuteOptions = @(0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50)
        $startMinute = $startMinuteOptions | Get-Random
        $duration = (Get-Random -Minimum 2 -Maximum 10) * 5
        $startTotal = ($startHour * 60) + $startMinute
        $endTotal = $startTotal + $duration
        $endHour = [Math]::Floor($endTotal / 60)
        $endMinute = $endTotal % 60
        if ($endHour -gt 12) { $endHour -= 12 }
        $startText = "{0}:{1:D2}" -f $startHour, $startMinute
        $endText = "{0}:{1:D2}" -f $endHour, $endMinute
        Add-IntegerQuestion `
            -QuestionText "Concept: The length of time between two clock times is called elapsed time. Question: A lesson starts at $startText and ends at $endText. How many minutes long is the lesson?" `
            -Correct $duration `
            -CandidateDistractors @(($duration + 5), ([Math]::Max(5, $duration - 5)), ($endMinute)) `
            -TimeLimit 35 `
            -Suffix "minutes"
    }

    $measurementQuestions = @(
        @{
            Question = "Concept: Liquid volume tells how much space a liquid takes up. Question: Which item is best measured by liquid volume?"
            Answers = @("a bottle of juice", "a backpack", "a basketball", "a desk")
        },
        @{
            Question = "Concept: Weight tells how heavy something is. Question: Which item is best measured by weight?"
            Answers = @("a bag of rice", "a cup of lemonade", "a fish tank of water", "a pitcher of juice")
        },
        @{
            Question = "Concept: Cups and gallons are units used for liquid volume. Question: Which unit would you most likely use to measure milk in a carton?"
            Answers = @("cups", "pounds", "feet", "inches")
        },
        @{
            Question = "Concept: Ounces and pounds are units used for weight. Question: Which unit would you most likely use to measure the weight of a dog?"
            Answers = @("pounds", "cups", "gallons", "minutes")
        },
        @{
            Question = "Concept: Choosing the correct attribute means deciding whether something should be measured by liquid volume or weight. Question: Which item would most likely be measured by liquid volume instead of weight?"
            Answers = @("soup in a pot", "a box of books", "a bowling ball", "a backpack")
        }
    )
    foreach ($entry in $measurementQuestions) {
        Add-Question `
            -QuestionText $entry.Question `
            -Answers $entry.Answers `
            -CorrectIndex 1 `
            -TimeLimit 20
    }
}

function Add-DataFinancialQuestions {
    $colors = @("red", "blue", "green", "yellow")
    for ($i = 0; $i -lt 10; $i++) {
        $counts = @(Get-UniqueRandomNumbers -Count 4 -Minimum 3 -Maximum 16)
        $total = ($counts | Measure-Object -Sum).Sum
        if ($i % 2 -eq 0) {
            Add-IntegerQuestion `
                -QuestionText "Concept: A frequency table shows how often each category appears. Question: A table shows $($colors[0]) = $($counts[0]), $($colors[1]) = $($counts[1]), $($colors[2]) = $($counts[2]), and $($colors[3]) = $($counts[3]). How many items are in the table altogether?" `
                -Correct $total `
                -CandidateDistractors @(($counts[0] + $counts[1]), ($counts[2] + $counts[3]), ($total + 4)) `
                -TimeLimit 35
        }
        else {
            $maxIndex = [Array]::IndexOf($counts, ($counts | Measure-Object -Maximum).Maximum)
            $minIndex = [Array]::IndexOf($counts, ($counts | Measure-Object -Minimum).Minimum)
            $difference = $counts[$maxIndex] - $counts[$minIndex]
            Add-IntegerQuestion `
                -QuestionText "Concept: Data in a table can be compared by finding how many more or fewer. Question: A table shows $($colors[0]) = $($counts[0]), $($colors[1]) = $($counts[1]), $($colors[2]) = $($counts[2]), and $($colors[3]) = $($counts[3]). How many more items are in the greatest category than in the least category?" `
                -Correct $difference `
                -CandidateDistractors @(($counts[$maxIndex]), ($counts[$minIndex]), ($difference + 2)) `
                -TimeLimit 35
        }
    }

    $symbols = @("star", "circle", "triangle", "square")
    for ($i = 0; $i -lt 10; $i++) {
        $value = Get-Random -Minimum 2 -Maximum 6
        $symbolCount = Get-Random -Minimum 2 -Maximum 8
        $correct = $value * $symbolCount
        if ($i % 2 -eq 0) {
            Add-IntegerQuestion `
                -QuestionText "Concept: In a pictograph, each symbol stands for a set number of items. Question: In a picture graph, each $($symbols[$i % $symbols.Count]) stands for $value books. One row has $symbolCount symbols. How many books does that row represent?" `
                -Correct $correct `
                -CandidateDistractors @(($value + $symbolCount), ($correct + $value), ($symbolCount)) `
                -TimeLimit 30
        }
        else {
            $secondCount = Get-Random -Minimum 1 -Maximum 6
            $sum = ($symbolCount + $secondCount) * $value
            Add-IntegerQuestion `
                -QuestionText "Concept: A pictograph can be used to combine data from more than one category. Question: In a picture graph, each symbol stands for $value votes. Category A has $symbolCount symbols and Category B has $secondCount symbols. How many votes do the two categories have altogether?" `
                -Correct $sum `
                -CandidateDistractors @(($symbolCount + $secondCount), ($symbolCount * $value), ($sum + $value)) `
                -TimeLimit 35
        }
    }

    for ($i = 0; $i -lt 5; $i++) {
        $monday = Get-Random -Minimum 8 -Maximum 20
        $tuesday = Get-Random -Minimum 8 -Maximum 20
        $wednesday = Get-Random -Minimum 8 -Maximum 20
        $goal = Get-Random -Minimum 6 -Maximum 12
        $aboveGoal = ($monday - $goal) + ($tuesday - $goal) + ($wednesday - $goal)
        Add-IntegerQuestion `
            -QuestionText "Concept: Data can answer multi-step questions by combining and comparing amounts. Question: A class read $monday books on Monday, $tuesday books on Tuesday, and $wednesday books on Wednesday. If the goal was $goal books each day, how many books above the 3-day goal did the class read?" `
            -Correct $aboveGoal `
            -CandidateDistractors @(($monday + $tuesday + $wednesday), ($goal * 3), ($aboveGoal + 3)) `
            -TimeLimit 40
    }

    $financialQuestions = @(
        @{
            Question = "Concept: Income is money a person earns for work. Question: Which example shows income?"
            Answers = @("getting paid for mowing lawns", "buying a game", "spending money at a store", "giving away a toy")
        },
        @{
            Question = "Concept: Labor is work people do to earn income. Question: Which action is an example of labor?"
            Answers = @("walking dogs for neighbors", "saving birthday money", "borrowing a pencil", "trading baseball cards")
        },
        @{
            Question = "Concept: People earn income when they provide goods or services. Question: Which job most directly provides a service?"
            Answers = @("washing cars", "selling a used toy", "saving coins in a jar", "collecting stamps")
        },
        @{
            Question = "Concept: A budget is a plan for how money will be used. Question: Why do people make a budget?"
            Answers = @("to plan spending and saving", "to make prices higher", "to turn coins into bills", "to avoid earning income")
        },
        @{
            Question = "Concept: Saving means keeping money to use later. Question: Which choice shows saving?"
            Answers = @("putting money in a jar for a bike", "spending all allowance today", "borrowing money for candy", "trading lunch for a toy")
        },
        @{
            Question = "Concept: Saving helps people reach a future spending goal. Question: Why might a student save part of each allowance?"
            Answers = @("to buy something bigger later", "to spend it twice today", "to avoid counting money", "to make prices disappear")
        },
        @{
            Question = "Concept: Scarcity means there is not enough of something for everyone who wants it. Question: Which situation shows scarcity?"
            Answers = @("3 markers for 6 students", "10 books for 3 readers", "20 apples for 4 families", "8 chairs for 5 people")
        },
        @{
            Question = "Concept: Because of scarcity, people make choices about what they want most. Question: If a store has only one last toy and many students want it, which word best describes the situation?"
            Answers = @("scarcity", "income", "deposit", "salary")
        },
        @{
            Question = "Concept: A choice has a cost when you give up one thing to get another. Question: If Maya spends her $5 on a puzzle instead of a ball, what is the cost of her choice?"
            Answers = @("she cannot use the $5 for the ball", "she earns extra money", "the puzzle becomes free", "the store gives her more toys")
        },
        @{
            Question = "Concept: Depositing money means putting money into savings. Question: Which action is a deposit?"
            Answers = @("putting $10 into a savings account", "taking $10 out to buy lunch", "borrowing $10 from a friend", "spending $10 on a game")
        },
        @{
            Question = "Concept: Withdrawing money means taking money out of savings. Question: Which action is a withdrawal?"
            Answers = @("taking money out of a savings account", "adding coins to a bank", "earning money for chores", "keeping money in an envelope")
        },
        @{
            Question = "Concept: Borrowing means using someone else's money now and paying it back later. Question: Which example shows borrowing?"
            Answers = @("using a library book and returning it later", "saving allowance in a jar", "earning money by raking leaves", "buying a snack with your own money")
        },
        @{
            Question = "Concept: Credit means a promise to pay for something later. Question: Which situation best matches credit?"
            Answers = @("buy now and pay later", "save now and buy later", "work now and get paid now", "trade toys with a friend")
        },
        @{
            Question = "Concept: Producers make or do things people want. Question: Which person is acting as a producer?"
            Answers = @("a baker selling bread", "a child buying bread", "a student saving allowance", "a shopper making a list")
        },
        @{
            Question = "Concept: Consumers buy or use goods and services. Question: Which person is acting as a consumer?"
            Answers = @("a family buying groceries", "a chef cooking meals for sale", "a farmer growing corn", "a worker repairing a roof")
        }
    )

    foreach ($entry in $financialQuestions) {
        Add-Question `
            -QuestionText $entry.Question `
            -Answers $entry.Answers `
            -CorrectIndex 1 `
            -TimeLimit 25
    }
}

Add-PlaceValueQuestions
Add-AdditionSubtractionQuestions
Add-MultiplicationDivisionQuestions
Add-FractionQuestions
Add-GeometryMeasurementQuestions
Add-DataFinancialQuestions

if ($questions.Count -ne 300) {
    throw "Expected 300 questions, but found $($questions.Count)."
}

$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add('"Question #","Question Text","Answer 1","Answer 2","Answer 3 (Optional)","Answer 4 (Optional)","Time Limit (sec) (Max: 300 seconds)","Correct Answer(s) (Only include Answer #)"') | Out-Null

for ($i = 0; $i -lt $questions.Count; $i++) {
    $entry = $questions[$i]
    $fields = @(
        (Convert-ToCsvField ($i + 1)),
        (Convert-ToCsvField $entry.question),
        (Convert-ToCsvField $entry.answers[0]),
        (Convert-ToCsvField $entry.answers[1]),
        (Convert-ToCsvField $entry.answers[2]),
        (Convert-ToCsvField $entry.answers[3]),
        (Convert-ToCsvField $entry.time),
        (Convert-ToCsvField $entry.correct)
    )
    $lines.Add(($fields -join ",")) | Out-Null
}

Set-Content -Path $OutputCsv -Value $lines -Encoding UTF8

Write-Host "Created: $OutputCsv"
Write-Host "Question count: $($questions.Count)"
