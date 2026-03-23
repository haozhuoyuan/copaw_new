import { useState } from "react";
import {
  Modal,
  Input,
  Button,
  message,
  Spin,
  Typography,
  Tag,
  Space,
} from "antd";
import { Plus, Sparkles, Bot, Wand2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { agentsApi } from "@/api/modules/agents";
// import type { GeneratedConfig } from "@/api/types/agents";
import styles from "./AgentCreatorModal.module.less";

const { Text } = Typography;
const { TextArea } = Input;

interface AgentCreatorModalProps {
  open: boolean;
  onSuccess: () => void;
  onCancel: () => void;
}

// Quick creation suggestions
const QUICK_SUGGESTIONS_ZH = [
  "创建一个代码书写智能体",
  "创建一个文案写作助手",
  "创建一个数据分析专家",
  "创建一个创意写作助手",
  "创建一个技术咨询顾问",
];

const QUICK_SUGGESTIONS_EN = [
  "Create a coding assistant",
  "Create a content writing helper",
  "Create a data analysis expert",
  "Create a creative writing assistant",
  "Create a technical consultant",
];

export default function AgentCreatorModal({
  open,
  onSuccess,
  onCancel,
}: AgentCreatorModalProps) {
  const { t, i18n } = useTranslation();
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);

  const isZh = i18n.language.startsWith("zh");
  const suggestions = isZh ? QUICK_SUGGESTIONS_ZH : QUICK_SUGGESTIONS_EN;

  const handleSuggestionClick = (suggestion: string) => {
    setDescription(suggestion);
  };

  const handleCreate = async () => {
    if (!description.trim()) {
      message.error(t("agentCreator.descriptionRequired"));
      return;
    }

    try {
      setLoading(true);
      const response = await agentsApi.createAgentFromText({
        description: description.trim(),
        language: i18n.language.startsWith("zh") ? "zh" : "en",
      });

      message.success(response.message);
      setDescription("");
      onSuccess();
    } catch (error: any) {
      console.error("Failed to create agent:", error);
      message.error(error.message || t("agentCreator.createFailed"));
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setDescription("");
    onCancel();
  };

  return (
    <Modal
      title={
        <Space>
          <Wand2 size={20} />
          <span>{t("agentCreator.modalTitle")}</span>
        </Space>
      }
      open={open}
      onCancel={handleCancel}
      width={600}
      footer={[
        <Button key="cancel" onClick={handleCancel}>
          {t("common.cancel")}
        </Button>,
        <Button
          key="create"
          type="primary"
          icon={<Plus size={16} />}
          loading={loading}
          onClick={handleCreate}
          disabled={!description.trim()}
        >
          {t("agent.create")}
        </Button>,
      ]}
    >
      <Spin spinning={loading}>
        <div className={styles.creatorContent}>
          {/* Description Input */}
          <div className={styles.inputSection}>
            <Text strong>{t("agentCreator.describeAgent")}</Text>
            <TextArea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder={t("agentCreator.placeholder")}
              rows={3}
              className={styles.descriptionInput}
              maxLength={200}
              showCount
            />
          </div>

          {/* Quick Suggestions */}
          <div className={styles.suggestionsSection}>
            <Text type="secondary" className={styles.suggestionsLabel}>
              {t("agentCreator.quickSuggestions")}
            </Text>
            <Space size={[8, 8]} wrap>
              {suggestions.map((suggestion, index) => (
                <Tag
                  key={index}
                  className={styles.suggestionTag}
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  <Sparkles size={12} />
                  {suggestion}
                </Tag>
              ))}
            </Space>
          </div>

          {/* Info Box */}
          <div className={styles.infoBox}>
            <Bot size={16} />
            <Text type="secondary" className={styles.infoText}>
              {t("agentCreator.infoText")}
            </Text>
          </div>
        </div>
      </Spin>
    </Modal>
  );
}
