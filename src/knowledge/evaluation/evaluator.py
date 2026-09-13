"""
NirmaanAI Phase 19: Retrieval Evaluator
Computes Precision@K, Recall@K, Mean Reciprocal Rank (MRR),
and Anti-Hallucination Rejection Rate over the benchmark dataset.
"""

from typing import Any, Dict, List
from src.knowledge.evaluation.benchmark_dataset import BENCHMARK_TEST_CASES, BenchmarkTestCase
from src.knowledge.retrieval.retriever import KnowledgeRetriever
from src.knowledge.schemas import RetrievalResult


class RetrievalEvaluator:
    """Evaluates KnowledgeRetriever precision, recall, ranking, and anti-hallucination rejection."""

    def __init__(self, retriever: KnowledgeRetriever, top_k: int = 5):
        self.retriever = retriever
        self.top_k = top_k

    def evaluate_benchmark(
        self, test_cases: List[BenchmarkTestCase] = BENCHMARK_TEST_CASES
    ) -> Dict[str, Any]:
        """
        Executes all benchmark queries and calculates retrieval evaluation metrics.
        """
        results: List[Dict[str, Any]] = []
        positive_recalls: List[float] = []
        positive_precisions: List[float] = []
        positive_reciprocal_ranks: List[float] = []
        negative_correct_rejections: int = 0
        total_negative: int = 0

        for case in test_cases:
            res: RetrievalResult = self.retriever.retrieve(
                query=case.query,
                top_k=self.top_k,
                include_retrospective=case.include_retrospective,
            )

            case_eval: Dict[str, Any] = {
                "query_id": case.query_id,
                "query": case.query,
                "is_negative": case.is_negative,
                "status": res.status,
                "expected_status": case.expected_status,
                "total_found": res.total_found,
                "execution_time_ms": res.execution_time_ms,
            }

            if case.is_negative:
                total_negative += 1
                is_correct = (res.status == "NO_SUFFICIENT_EVIDENCE")
                if is_correct:
                    negative_correct_rejections += 1
                case_eval["correct_rejection"] = is_correct
            else:
                # Evaluate positive domain query
                retrieved_sources = [it.source_id for it in res.items]
                retrieved_phases = [it.phase for it in res.items]
                retrieved_texts = " ".join(it.text for it in res.items)

                # Source-level hit check
                hits = [
                    (it.source_id in case.target_sources or it.phase in case.target_phases)
                    for it in res.items
                ]
                precision = (sum(hits) / len(hits)) if hits else 0.0
                recall = 1.0 if any(hits) else 0.0

                # MRR: reciprocal rank of first relevant hit
                rr = 0.0
                for rank, hit in enumerate(hits, start=1):
                    if hit:
                        rr = 1.0 / rank
                        break

                # Verify expected key terms presence
                terms_matched = [term.lower() in retrieved_texts.lower() for term in case.expected_terms]
                all_terms_found = all(terms_matched) if terms_matched else True

                positive_precisions.append(precision)
                positive_recalls.append(recall)
                positive_reciprocal_ranks.append(rr)

                case_eval["precision"] = round(precision, 4)
                case_eval["recall"] = round(recall, 4)
                case_eval["reciprocal_rank"] = round(rr, 4)
                case_eval["all_terms_found"] = all_terms_found
                case_eval["retrieved_sources"] = retrieved_sources

            results.append(case_eval)

        # Compute aggregate metrics
        mean_precision = (sum(positive_precisions) / len(positive_precisions)) if positive_precisions else 0.0
        mean_recall = (sum(positive_recalls) / len(positive_recalls)) if positive_recalls else 0.0
        mrr = (sum(positive_reciprocal_ranks) / len(positive_reciprocal_ranks)) if positive_reciprocal_ranks else 0.0
        rejection_rate = (negative_correct_rejections / total_negative) if total_negative > 0 else 1.0

        summary = {
            "total_queries_evaluated": len(test_cases),
            "positive_queries_count": len(positive_recalls),
            "negative_queries_count": total_negative,
            "mean_precision_at_k": round(mean_precision, 4),
            "mean_recall_at_k": round(mean_recall, 4),
            "mrr": round(mrr, 4),
            "anti_hallucination_rejection_rate": round(rejection_rate, 4),
            "all_negative_rejected": (negative_correct_rejections == total_negative),
            "results": results,
        }
        return summary
